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
#import "SearchEntitiesAutoSuggestCell.h"
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
  ResultTypeFull,
  ResultTypeLocal
} ResultType;


@interface SearchEntitiesViewController ()
- (void)createFilterBar;
- (void)filterButtonPressed:(id)sender;
- (void)textFieldDidChange:(id)sender;
- (void)sendSearchRequest;
- (void)sendFastSearchRequest;
- (void)reloadTableData;

@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, retain) CLLocationManager* locationManager;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@property (nonatomic, retain) RKRequest* currentRequest;
@property (nonatomic, assign) ResultType currentResultType;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, readonly) UIButton* clearFilterButton;
@property (nonatomic, assign) SearchFilter currentSearchFilter;
@property (nonatomic, retain) UIView* filterBar;
@end

@implementation SearchEntitiesViewController

@synthesize resultsArray = resultsArray_;
@synthesize searchField = searchField_;
@synthesize locationButton = locationButton_;
@synthesize locationManager = locationManager_;
@synthesize addStampCell = addStampCell_;
@synthesize addStampLabel = addStampLabel_;
@synthesize tooltipImageView = tooltipImageView_;
@synthesize searchingIndicatorCell = searchingIndicatorCell_;
@synthesize currentRequest = currentRequest_;
@synthesize currentResultType = currentResultType_;
@synthesize loading = loading_;
@synthesize loadingIndicatorLabel = loadingIndicatorLabel_;
@synthesize currentSearchFilter = currentSearchFilter_;
@synthesize searchIntent = searchIntent_;
@synthesize clearFilterButton = clearFilterButton_;
@synthesize tableView = tableView_;
@synthesize filterBar = filterBar_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.resultsArray = nil;
  self.searchField = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorCell = nil;
  self.currentRequest = nil;
  self.locationButton = nil;
  self.loadingIndicatorLabel = nil;
  self.tableView = nil;
  self.filterBar = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [self.searchField addTarget:self
                       action:@selector(textFieldDidChange:)
             forControlEvents:UIControlEventEditingChanged];

  self.locationManager = [[[CLLocationManager alloc] init] autorelease];
  self.locationManager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters;
  
  tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_tooltip"]];
  tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame, 5, 40);
  tooltipImageView_.alpha = 0.0;
  [self.view addSubview:tooltipImageView_];
  [tooltipImageView_ release];
  self.searchingIndicatorCell.selectionStyle = UITableViewCellSelectionStyleNone;
  [self createFilterBar];
}

- (void)createFilterBar {
  filterBar_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  filterBar_.backgroundColor = [UIColor colorWithWhite:0.4 alpha:1.0];
  CAGradientLayer* gradient = [[CAGradientLayer alloc] init];
  gradient.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.6 alpha:1.0].CGColor,
                                              (id)[UIColor colorWithWhite:0.5 alpha:1.0].CGColor, nil];
  gradient.startPoint = CGPointZero;
  gradient.endPoint = CGPointMake(0, 1);
  gradient.frame = CGRectMake(0, 1, 320, 43);
  // This is not providing the right amount of opacity.
  gradient.opacity = 0.95;
  [filterBar_.layer addSublayer:gradient];
  [gradient release];
  
  NSUInteger i = 0;
  const CGFloat yDistance = 42.0;
  // Food.
  UIButton* filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_restaurants_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_restaurants_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterFood;
  [filterBar_ addSubview:filterButton];
  // Book.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_books_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_books_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterBook;
  [filterBar_ addSubview:filterButton];
  // Film.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_movies_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_movies_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterFilm;
  [filterBar_ addSubview:filterButton];
  // Music.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_music_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_music_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterMusic;
  [filterBar_ addSubview:filterButton];
  // Other.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_other_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"sea_filter_other_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  filterButton.tag = SearchFilterOther;
  [filterBar_ addSubview:filterButton];
  // None.
  ++i;
  clearFilterButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"sea_filter_clear_button"]
                      forState:UIControlStateNormal];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"sea_filter_clear_button_selected"]
                      forState:UIControlStateSelected];
  clearFilterButton_.frame = CGRectMake(5 + (yDistance * i), 3, 40, 40);
  clearFilterButton_.tag = SearchFilterNone;
  clearFilterButton_.alpha = 0.0;
  [filterBar_ addSubview:clearFilterButton_];

  for (UIView* view in filterBar_.subviews) {
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
  self.loadingIndicatorLabel = nil;
  self.locationButton = nil;
  self.tableView = nil;
  self.filterBar = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  
  switch (self.searchIntent) {
    case SearchIntentStamp:
      searchField_.placeholder = locationButton_.selected ? @"Search nearby" : @"Find something to stamp";
      break;
    case SearchIntentTodo:
      self.searchField.placeholder = @"Find something to do...";
      break;
    default:
      break;
  }

  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self.locationManager startUpdatingLocation];
  if (self.searchField.text.length == 0 && currentResultType_ != ResultTypeLocal) {
    [UIView animateWithDuration:0.3 animations:^{
      tooltipImageView_.alpha = 1.0;
    }];
    [searchField_ becomeFirstResponder];
  }
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  if (self.searchField.text.length == 0)
    tooltipImageView_.alpha = 0.0;

  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  loading_ = NO;
  if (self.navigationController.viewControllers.count > 1)
    [self.navigationController setNavigationBarHidden:NO animated:animated];

  [self.locationManager stopUpdatingLocation];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  [self reloadTableData];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)locationButtonTapped:(id)sender {
  UIButton* locationButton = sender;
  locationButton.selected = !locationButton.selected;
  switch (self.searchIntent) {
    case SearchIntentStamp:
      searchField_.placeholder = locationButton_.selected ? @"Search nearby" : @"Find something to stamp";
      break;
    case SearchIntentTodo:
      self.searchField.placeholder = @"Find something to do...";
      break;
    default:
      break;
  }

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     tooltipImageView_.alpha = (self.searchField.text.length > 0 || locationButton.selected) ? 0 : 1;
                   }
                   completion:nil];

  if (locationButton.selected) {
    currentSearchFilter_ = SearchFilterNone;
    currentResultType_ = ResultTypeLocal;
    [self sendSearchRequest];
  } else {
    currentResultType_ = ResultTypeFast;
    [searchField_ becomeFirstResponder];
    [self reloadTableData];
  }
}

- (IBAction)cancelButtonTapped:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

- (void)filterButtonPressed:(id)sender {
  UIButton* button = sender;
  for (UIView* view in tableView_.tableHeaderView.subviews) {
    if ([view isMemberOfClass:[UIButton class]] && view != sender)
      [(UIButton*)view setSelected:NO];
  }

  self.currentSearchFilter = button.tag;

  if (self.currentSearchFilter != SearchFilterNone)
    button.selected = !button.selected;
  else if (self.currentSearchFilter == SearchFilterNone)
    button.selected = NO;

  if (!button.selected)
    currentSearchFilter_ = SearchFilterNone;
  
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                   animations:^{ clearFilterButton_.alpha = currentSearchFilter_ == SearchFilterNone ? 0 : 1; }
                   completion:nil];
  
  //if (searchField_.text.length)
  //  [self sendSearchRequest];
}

- (void)reloadTableData {
  tableView_.hidden = resultsArray_.count == 0 && currentResultType_ != ResultTypeFull;
  if (currentResultType_ == ResultTypeFast || resultsArray_.count == 0)
    tableView_.tableHeaderView = nil;
  else
    tableView_.tableHeaderView = filterBar_;

  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (searchField_.text.length == 0 && currentResultType_ != ResultTypeLocal)
    return 0;

  // Return the number of rows in the section.
  NSInteger numRows = [resultsArray_ count];
  if (currentResultType_ == ResultTypeFull && !loading_)
    ++numRows;  // One more for the 'Add new entity' cell.
  if (loading_)
    ++numRows;  // For the 'Loading...' cell.

  return numRows;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (currentResultType_ == ResultTypeFast) {
    static NSString* CellIdentifier = @"AutoSuggestCell";
    SearchEntitiesAutoSuggestCell* cell =
        (SearchEntitiesAutoSuggestCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
      cell = [[[SearchEntitiesAutoSuggestCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

    SearchResult* result = [resultsArray_ objectAtIndex:indexPath.row];
    cell.textLabel.text = result.title;
    return cell;
  }
  
  if (indexPath.row == [resultsArray_ count] && currentResultType_ == ResultTypeFull && !loading_)
    return self.addStampCell;
  
  if (indexPath.row == 0 && currentResultType_ == ResultTypeLocal && loading_)
    return self.searchingIndicatorCell;
  
  if (indexPath.row == resultsArray_.count && currentResultType_ == ResultTypeLocal && searchField_.text.length > 0)
    return self.addStampCell;

  if (indexPath.row == 0 && (currentResultType_ == ResultTypeFull || currentResultType_ == ResultTypeLocal) && loading_)
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

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  self.currentResultType = ResultTypeFast;
  self.resultsArray = nil;
  [self reloadTableData];
  return YES;
}

- (void)sendFastSearchRequest {
  self.currentResultType = ResultTypeFast;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
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
  if (self.currentResultType != ResultTypeLocal) {
    self.currentResultType = ResultTypeFull;
    switch (currentSearchFilter_) {
      case SearchFilterBook:
        loadingIndicatorLabel_.text = @"Searching books...";
        break;
      case SearchFilterFood:
        loadingIndicatorLabel_.text = @"Searching restaurants & bars...";
        break;
      case SearchFilterMusic:
        loadingIndicatorLabel_.text = @"Searching music...";
        break;
      case SearchFilterFilm:
        loadingIndicatorLabel_.text = @"Searching movies & TV shows...";
        break;
      case SearchFilterOther:
      case SearchFilterNone:
      default:
        loadingIndicatorLabel_.text = @"Searching...";
        break;
    }
  } else if (currentResultType_ == ResultTypeLocal && searchField_.text.length == 0) {
    loadingIndicatorLabel_.text = @"Loading popular results nearby";
  } else if (currentResultType_ == ResultTypeLocal) {
    loadingIndicatorLabel_.text = @"Searching nearby...";
  }

  loading_ = YES;
  self.resultsArray = nil;
  [self reloadTableData];
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* searchResultMapping = [objectManager.mappingProvider mappingForKeyPath:@"SearchResult"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kSearchPath delegate:self];
  objectLoader.objectMapping = searchResultMapping;
  NSString* query = searchField_.text;
  if (!query.length)
    query = @" ";

  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithKeysAndObjects:@"q", query, nil];
  if (self.locationManager.location) {
    CLLocationCoordinate2D coordinate = self.locationManager.location.coordinate;
    NSString* coordString = [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
    [params setObject:coordString forKey:@"coordinates"];
  }

  if (currentSearchFilter_ != SearchFilterNone)
    [params setObject:kSearchFilterStrings[currentSearchFilter_] forKey:@"category"];
  
  if (currentResultType_ == ResultTypeLocal)
    [params setObject:@"true" forKey:@"local"];

  objectLoader.params = params;
  [objectLoader send];
  self.currentRequest = objectLoader;
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  loading_ = NO;
  if ([request.URL.absoluteString rangeOfString:kFastSearchURI].location == NSNotFound)
    return;

  NSLog(@"Fast search url: %@", request.URL.absoluteString);
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
    if (currentSearchFilter_ != SearchFilterNone) {
      NSPredicate* predicate = [NSPredicate predicateWithFormat:@"category == %@",
          kSearchFilterStrings[currentSearchFilter_]];
      self.resultsArray = [array filteredArrayUsingPredicate:predicate];
    } else {
      self.resultsArray = array;
    }
    [self reloadTableData];
  } else if (response.isNotFound) {
    self.resultsArray = nil;
    [self reloadTableData];
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSLog(@"response: %@", objectLoader.response.bodyAsString);
  loading_ = NO;
  self.resultsArray = objects;
  [self reloadTableData];
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
  [self reloadTableData];
}

#pragma mark - UITableViewDelegate Methods.

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  if (!resultsArray_.count || currentResultType_ == ResultTypeFast)
    return 0;

  return 25;
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (currentResultType_ == ResultTypeFast)
    return 47.0;

  return 63.0;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
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
  if (resultsArray_ && resultsArray_.count == 0) {
    view.leftLabel.text = @"No results";
  } else if (currentResultType_ == ResultTypeLocal) {
    view.leftLabel.text = searchField_.text.length ? @"Nearby results" : @"Popular nearby";
  } else {
    NSString* corpus = @"All results";
    switch (currentSearchFilter_) {
      case SearchFilterBook:
        corpus = @"Book results";
        break;
      case SearchFilterMusic:
        corpus = @"Music results";
        break;
      case SearchFilterFilm:
        corpus = @"Movie & TV show results";
        break;
      case SearchFilterFood:
        corpus = @"Restaurant & bar results";
        break;
      case SearchFilterOther:
        corpus = @"Other category results";
        break;
      default:
        break;
    }
    view.leftLabel.text = corpus;
  }
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (currentResultType_ == ResultTypeFast) {
    self.searchField.text = [(SearchResult*)[resultsArray_ objectAtIndex:indexPath.row] title];
    [self sendSearchRequest];
    return;
  }
  
  SearchResult* result = nil;
  if (indexPath.row == [resultsArray_ count] && currentResultType_ == ResultTypeFull) {
    result = [[[SearchResult alloc] init] autorelease];
    result.title = self.searchField.text;
  } else if (indexPath.row == 0 && currentResultType_ == ResultTypeLocal && !loading_ && searchField_.text.length > 0 && resultsArray_.count == 0) {
    [self.tableView deselectRowAtIndexPath:indexPath animated:YES];
    [self sendSearchRequest];
    return;
  } else if (indexPath.row == resultsArray_.count && currentResultType_ == ResultTypeLocal) {
    if (searchField_.text.length > 0) {
      result = [[[SearchResult alloc] init] autorelease];
      result.title = self.searchField.text;
    } else {
      [self.tableView deselectRowAtIndexPath:indexPath animated:YES];
      [self.tableView setContentOffset:CGPointMake(0, 0) animated:NO];
      [searchField_ becomeFirstResponder];
      return;
    }
  } else if (currentResultType_ == ResultTypeFast) {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row];
  } else if ((currentResultType_ == ResultTypeFull || currentResultType_ == ResultTypeLocal) && !loading_) {
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
      break;
    }
    default:
      break;
  }
}

- (void)resetState {
  self.currentResultType = ResultTypeFast;
  self.currentSearchFilter = SearchFilterNone;
  self.currentRequest = nil;
  self.searchField.text = nil;
  self.locationButton.selected = NO;
  [self textFieldDidChange:self.searchField];
  //if (!searchField_.inputAccessoryView)
    //[self addKeyboardAccessoryView];
  //else
  //  [self filterButtonPressed:nil];
}

- (void)textFieldDidChange:(id)sender {
  if (sender != self.searchField)
    return;

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     tooltipImageView_.alpha = (self.searchField.text.length > 0 || locationButton_.selected) ? 0.0 : 1.0;
                   }
                   completion:nil];

  self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
  if (searchField_.text.length > 0 && currentResultType_ != ResultTypeLocal) {
    [self sendFastSearchRequest];
  } else {
    [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
    self.resultsArray = nil;
    [self reloadTableData];
  }
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [searchField_ resignFirstResponder];
}

@end
