//
//  SearchEntitiesViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesViewController.h"

#import <CoreLocation/CoreLocation.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "EntityDetailViewController.h"
#import "SearchEntitiesTableViewCell.h"
#import "STSearchField.h"
#import "STSectionHeaderView.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"
#import "Util.h"

static NSString* const kSearchPath = @"/entities/search.json";
static NSString* const kFastSearchURI = @"http://static.stamped.com/search/v1/";

typedef enum {
  SearchFilterNone = 0,
  SearchFilterFood,
  SearchFilterBook,
  SearchFilterFilm,
  SearchFilterMusic,
  SearchFilterOther
} SearchFilter;

// This MUST be kept in sync with the enum order above.

NSString* const kSearchFilterStrings[6] = {
  @"",
  @"food",
  @"book",
  @"film",
  @"music",
  @"other"
};

typedef enum {
  ResultTypeFast,
  ResultTypeFull
} ResultType;


@interface SearchEntitiesViewController ()
- (void)addKeyboardAccessoryView;
- (void)filterButtonPressed:(id)sender;
- (void)textFieldDidChange:(id)sender;
- (void)sendSearchRequest;
- (void)sendFastSearchRequest;

@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, retain) CLLocationManager* locationManager;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@property (nonatomic, retain) RKRequest* currentRequest;
@property (nonatomic, assign) ResultType currentResultType;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, readonly) UIButton* clearFilterButton;
@property (nonatomic, assign) SearchFilter currentSearchFilter;
@end

@implementation SearchEntitiesViewController

@synthesize resultsArray = resultsArray_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;
@synthesize locationManager = locationManager_;
@synthesize addStampCell = addStampCell_;
@synthesize addStampLabel = addStampLabel_;
@synthesize tooltipImageView = tooltipImageView_;
@synthesize searchingIndicatorCell = searchingIndicatorCell_;
@synthesize currentRequest = currentRequest_;
@synthesize currentResultType = currentResultType_;
@synthesize fullSearchCellLabel = fullSearchCellLabel_;
@synthesize fullSearchCell = fullSearchCell_;
@synthesize loading = loading_;
@synthesize loadingIndicatorLabel = loadingIndicatorLabel_;
@synthesize currentSearchFilter = currentSearchFilter_;
@synthesize searchIntent = searchIntent_;
@synthesize clearFilterButton = clearFilterButton_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.resultsArray = nil;
  self.searchField = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.fullSearchCellLabel = nil;
  self.searchingIndicatorCell = nil;
  self.currentRequest = nil;
  self.fullSearchCell = nil;
  self.loadingIndicatorLabel = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.view.backgroundColor = [UIColor colorWithWhite:0.972 alpha:1.0];
  self.cancelButton.layer.masksToBounds = YES;
  self.cancelButton.layer.borderColor = [UIColor colorWithWhite:0.6 alpha:0.8].CGColor;
  self.cancelButton.layer.borderWidth = 1.0;
  self.cancelButton.layer.cornerRadius = 5.0;
  self.cancelButton.layer.shadowOpacity = 1.0;

  [self.searchField addTarget:self
                       action:@selector(textFieldDidChange:)
             forControlEvents:UIControlEventEditingChanged];

  self.locationManager = [[[CLLocationManager alloc] init] autorelease];
  self.locationManager.desiredAccuracy = kCLLocationAccuracyKilometer;
  
  tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_tooltip"]];
  tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame, 5, 40);
  tooltipImageView_.alpha = 0.0;
  [self.view addSubview:tooltipImageView_];
  [tooltipImageView_ release];
  self.searchingIndicatorCell.selectionStyle = UITableViewCellSelectionStyleNone;
  [self addKeyboardAccessoryView];
}

- (void)addKeyboardAccessoryView {
  UIView* accessoryView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  accessoryView.backgroundColor = [UIColor colorWithWhite:0.4 alpha:1.0];
  accessoryView.alpha = 0.95;
  CAGradientLayer* gradient = [[CAGradientLayer alloc] init];
  gradient.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.15 alpha:1.0].CGColor,
                     (id)[UIColor colorWithWhite:0.3 alpha:1.0].CGColor, nil];
  gradient.startPoint = CGPointZero;
  gradient.endPoint = CGPointMake(0, 1);
  gradient.frame = CGRectMake(0, 1, 320, 43);
  // This is not providing the right amount of opacity.
  gradient.opacity = 0.95;
  [accessoryView.layer addSublayer:gradient];
  [gradient release];
  searchField_.inputAccessoryView = accessoryView;
  [accessoryView release];
  
  NSUInteger i = 0;
  const CGFloat yDistance = 42.0;
  // Food.
  UIButton* filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_restaurants_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_restaurants_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterFood;
  [accessoryView addSubview:filterButton];
  // Book.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_books_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_books_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterBook;
  [accessoryView addSubview:filterButton];
  // Film.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_movies_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_movies_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterFilm;
  [accessoryView addSubview:filterButton];
  // Music.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_music_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_music_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterMusic;
  [accessoryView addSubview:filterButton];
  // Other.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_other_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"keyb_filter_other_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterOther;
  [accessoryView addSubview:filterButton];
  // None.
  ++i;
  clearFilterButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"keyb_filter_clear_button"]
                      forState:UIControlStateNormal];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"keyb_filter_clear_button_selected"]
                      forState:UIControlStateSelected];
  clearFilterButton_.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  clearFilterButton_.tag = SearchFilterNone;
  clearFilterButton_.alpha = 0.0;
  [accessoryView addSubview:clearFilterButton_];

  for (UIView* view in accessoryView.subviews) {
    if ([view isMemberOfClass:[UIButton class]]) {
      [(UIButton*)view addTarget:self
                          action:@selector(filterButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
    }
  }
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.searchField = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorCell = nil;
  self.fullSearchCell = nil;
  self.fullSearchCellLabel = nil;
  self.loadingIndicatorLabel = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  
  switch (self.searchIntent) {
    case 0:
      self.searchField.placeholder = @"Find something to stamp...";
      break;
    case 1:
      self.searchField.placeholder = @"Find something to do...";
      break;
    default:
      self.searchField.placeholder = @"Find something to stamp...";
      break;
  }
  
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self.locationManager startUpdatingLocation];
  [self.searchField becomeFirstResponder];
  if (self.searchField.text.length == 0) {
    [UIView animateWithDuration:0.3 animations:^{
      tooltipImageView_.alpha = 1.0;
    }];
  }
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  if (self.searchField.text.length == 0)
    tooltipImageView_.alpha = 0.0;

  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  loading_ = NO;
  [self.navigationController setNavigationBarHidden:NO animated:animated];
  [self.locationManager stopUpdatingLocation];
}

- (void)viewDidDisappear:(BOOL)animated {
  [self.tableView reloadData];
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)cancelButtonTapped:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

- (void)filterButtonPressed:(id)sender {
  UIButton* button = sender;
  for (UIView* view in searchField_.inputAccessoryView.subviews) {
    if ([view isMemberOfClass:[UIButton class]] && view != sender)
      [(UIButton*)view setSelected:NO];
  }

  self.currentSearchFilter = button.tag;

  if (self.currentSearchFilter != SearchFilterNone)
    button.selected = !button.selected;
  else if (self.currentSearchFilter == SearchFilterNone)
    button.selected = NO;

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                   animations:^{ clearFilterButton_.alpha = currentSearchFilter_ == SearchFilterNone ? 0 : 1; }
                   completion:nil];
  
  if (searchField_.text.length) {
    if (currentResultType_ == ResultTypeFast)
      [self sendFastSearchRequest];
    else if (currentResultType_ == ResultTypeFull)
      [self sendSearchRequest];
  }
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (searchField_.text.length == 0)
    return 0;

  // Return the number of rows in the section.
  NSInteger numRows = [resultsArray_ count];
  if (currentResultType_ == ResultTypeFull && !loading_)
    ++numRows;  // One more for the 'Add new entity' cell.
  if (currentResultType_ == ResultTypeFast)
    ++numRows;  // For 'Search "blah"' cell.
  if (loading_)
    ++numRows;  // For the 'Loading...' cell.

  return numRows;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == [resultsArray_ count] && currentResultType_ == ResultTypeFull && !loading_)
    return self.addStampCell;

  if (indexPath.row == 0 && currentResultType_ == ResultTypeFast) {
    self.fullSearchCellLabel.text = [NSString stringWithFormat:@"Search for \u201c%@\u201d", searchField_.text];
    return self.fullSearchCell;
  }

  if (indexPath.row == 0 && currentResultType_ == ResultTypeFull && loading_)
    return self.searchingIndicatorCell;

  if (indexPath.row == 1 && currentResultType_ == ResultTypeFast && loading_)
    return self.searchingIndicatorCell;
  
  static NSString* CellIdentifier = @"ResultCell";
  SearchEntitiesTableViewCell* cell =
      (SearchEntitiesTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[SearchEntitiesTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  NSUInteger offset = 0;
  if (loading_)
    ++offset;
  
  if (currentResultType_ == ResultTypeFast)
    ++offset;

  NSUInteger index = indexPath.row - offset;
  [cell setSearchResult:(SearchResult*)[resultsArray_ objectAtIndex:index]];
  
  return cell;
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != searchField_)
    return YES;

  [self sendSearchRequest];
  [searchField_ resignFirstResponder];
  return NO;
}

- (void)sendFastSearchRequest {
  loadingIndicatorLabel_.text = @"Loading...";
  loading_ = YES;
  self.currentResultType = ResultTypeFast;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.resultsArray = nil;
  [self.tableView reloadData];
  NSString* query = self.searchField.text;
  query = [query lowercaseString];
  query = [query stringByReplacingOccurrencesOfString:@" " withString:@"_"];
  NSString* URLString = [NSString stringWithFormat:@"%@%@.json.gz", kFastSearchURI, query];
  if (currentSearchFilter_ != SearchFilterNone) {
    NSString* queryString = [NSString stringWithFormat:@"?category=%@", kSearchFilterStrings[currentSearchFilter_]];
    URLString = [URLString stringByAppendingString:queryString];
  }
  NSURL* url = [NSURL URLWithString:URLString];
  RKRequest* request = [[RKRequest alloc] initWithURL:url delegate:self];
  [[RKClient sharedClient].requestQueue addRequest:request];
  self.currentRequest = request;
  [request release];
}

- (void)sendSearchRequest {
  [searchField_ resignFirstResponder];
  loadingIndicatorLabel_.text = @"Searching...";
  loading_ = YES;
  self.currentResultType = ResultTypeFull;
  self.resultsArray = nil;
  [self.tableView reloadData];
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* searchResultMapping = [objectManager.mappingProvider mappingForKeyPath:@"SearchResult"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kSearchPath delegate:self];
  objectLoader.objectMapping = searchResultMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithKeysAndObjects:@"q", searchField_.text, nil];
  if (self.locationManager.location) {
    CLLocationCoordinate2D coordinate = self.locationManager.location.coordinate;
    NSString* coordString = [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
    [params setObject:coordString forKey:@"coordinates"];
  }

  if (currentSearchFilter_ != SearchFilterNone)
    [params setObject:kSearchFilterStrings[currentSearchFilter_] forKey:@"category"];

  objectLoader.params = params;
  [objectLoader send];
  self.currentRequest = objectLoader;
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  loading_ = NO;

  NSLog(@"Fast search url: %@", request.URL.absoluteString);
  if ([request.URL.absoluteString rangeOfString:kFastSearchURI].location == NSNotFound)
    return;

  if (response.isOK) {
    NSError* err = nil;
    id body = [response parsedBody:&err];
    if (err) {
      NSLog(@"Parse error for response %@: %@", response, err);
      return;
    }
    NSMutableArray* array = [NSMutableArray arrayWithCapacity:10];
    for (NSUInteger i = 0; i < MIN(10, [body count]); ++i) {
      id object = [body objectAtIndex:i];
      SearchResult* result = [[[SearchResult alloc] init] autorelease];
      result.title = [object valueForKey:@"title"];
      result.category = [object valueForKey:@"category"];
      result.subtitle = [object valueForKey:@"subtitle"];
      result.searchID = [object valueForKey:@"search_id"];
      result.entityID = [object valueForKey:@"entity_id"];
      [array addObject:result];
    }
    self.resultsArray = array;
    [self.tableView reloadData];
  } else if (response.isNotFound) {
    self.resultsArray = nil;
    [self.tableView reloadData];
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  loading_ = NO;
  self.currentResultType = ResultTypeFull;
  self.resultsArray = objects;
  [self.tableView reloadData];
  self.currentRequest = nil;
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  loading_ = NO;
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
  } else if ([objectLoader.response isNotFound]) {
    self.currentRequest = nil;
    [self sendSearchRequest];
    return;
  }
  [searchField_ becomeFirstResponder];
  self.currentRequest = nil;
}

#pragma mark - UITableViewDelegate Methods.

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  if (!resultsArray_.count || currentResultType_ == ResultTypeFast)
    return 0;

  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  if (self.resultsArray.count == 0)
    return nil;

  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  gradientLayer.frame = view.frame;
  gradientLayer.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.70 alpha:1.0].CGColor,
                                (id)[UIColor colorWithWhite:0.76 alpha:1.0].CGColor, nil];
  [view.layer insertSublayer:gradientLayer below:view.leftLabel.layer];
  [gradientLayer release];
  view.leftLabel.textColor = view.leftLabel.shadowColor;
  view.leftLabel.shadowColor = [UIColor stampedGrayColor];
  view.leftLabel.shadowOffset = CGSizeMake(0, -1);
  view.leftLabel.text = @"All results";
  return view;
}

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  SearchResult* result = nil;
  if (indexPath.row == [resultsArray_ count] && currentResultType_ == ResultTypeFull) {
    result = [[[SearchResult alloc] init] autorelease];
    result.title = self.searchField.text;
  } else if (indexPath.row == 0 && currentResultType_ == ResultTypeFast) {
    [self.tableView deselectRowAtIndexPath:indexPath animated:YES];
    [self sendSearchRequest];
    return;
  } else if (indexPath.row == 1 && currentResultType_ == ResultTypeFast && loading_) {
    return;
  } else if (currentResultType_ == ResultTypeFast && !loading_) {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row - 1];
  } else if (currentResultType_ == ResultTypeFast && loading_) {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row - 2];
  } else if (currentResultType_ == ResultTypeFull && !loading_) {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row];
  } else if (indexPath.row == 0 && currentResultType_ == ResultTypeFull && loading_) {
    return;
  }
  
  switch (self.searchIntent) {
    case SearchIntentStamp: {
      CreateStampViewController* detailViewController = [[CreateStampViewController alloc] initWithSearchResult:result];
      [self.navigationController pushViewController:detailViewController animated:YES];
      [detailViewController release];
      break;
    }
    case SearchIntentTodo: {
      EntityDetailViewController* detailViewController = (EntityDetailViewController*)[Util detailViewControllerForSearchResult:result];
      [detailViewController addToolbar];
      [self.navigationController pushViewController:detailViewController animated:YES];
//      [detailViewController release];
      break;
    }
    default:
      break;
  }

}

- (void)clearSearchField {
  self.searchField.text = nil;
  [self textFieldDidChange:self.searchField];
}

- (void)textFieldDidChange:(id)sender {
  if (sender != self.searchField)
    return;

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     tooltipImageView_.alpha = self.searchField.text.length > 0 ? 0.0 : 1.0;
                   }
                   completion:nil];

  self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
  if (searchField_.text.length > 0) {
    [self sendFastSearchRequest];
  } else {
    [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
    self.resultsArray = nil;
    [self.tableView reloadData];
  }
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [searchField_ resignFirstResponder];
}

@end
