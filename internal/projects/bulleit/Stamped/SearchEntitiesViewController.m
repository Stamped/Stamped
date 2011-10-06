//
//  SearchEntitiesViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "SearchEntitiesTableViewCell.h"
#import "STSearchField.h"
#import "STSectionHeaderView.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"

static NSString* const kSearchPath = @"/entities/search.json";
static NSString* const kFastSearchURI = @"http://static.stamped.com/search/v1/";

typedef enum {
  ResultTypeFast,
  ResultTypeFull
} ResultType;

@interface SearchEntitiesViewController ()
- (void)textFieldDidChange:(id)sender;
- (void)sendSearchRequest;
- (void)sendFastSearchRequest;

@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, retain) CLLocationManager* locationManager;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@property (nonatomic, retain) RKRequest* currentRequest;
@property (nonatomic, assign) ResultType currentResultType;
@end

@implementation SearchEntitiesViewController

@synthesize resultsArray = resultsArray_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;
@synthesize locationManager = locationManager_;
@synthesize addStampCell = addStampCell_;
@synthesize addStampLabel = addStampLabel_;
@synthesize tooltipImageView = tooltipImageView_;
@synthesize searchingIndicatorView = searchingIndicatorView_;
@synthesize currentRequest = currentRequest_;
@synthesize currentResultType = currentResultType_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.resultsArray = nil;
  self.searchField = nil;
  self.locationManager.delegate = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorView = nil;
  self.currentRequest = nil;
  tooltipImageView_ = nil;
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
  
  tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_tooltip"]];
  tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame, 6, 40);
  tooltipImageView_.alpha = 0.0;
  [self.view addSubview:tooltipImageView_];
  [tooltipImageView_ release];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.searchField = nil;
  self.locationManager.delegate = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorView = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  tooltipImageView_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
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
  [self.navigationController setNavigationBarHidden:NO animated:animated];
  [self.locationManager stopUpdatingLocation];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)cancelButtonTapped:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  NSInteger numRows = [resultsArray_ count];
  if (self.searchField.text.length > 0 && currentResultType_ == ResultTypeFull)
    ++numRows;  // One more for the 'Add new entity' cell.

  return numRows;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == [resultsArray_ count])
    return self.addStampCell;
  
  static NSString* CellIdentifier = @"ResultCell";
  SearchEntitiesTableViewCell* cell =
      (SearchEntitiesTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[SearchEntitiesTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  [cell setSearchResult:(SearchResult*)[resultsArray_ objectAtIndex:indexPath.row]];
  
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
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  NSString* query = self.searchField.text;
  query = [query lowercaseString];
  query = [query stringByReplacingOccurrencesOfString:@" " withString:@"_"];
  NSURL* url = [NSURL URLWithString:[NSString stringWithFormat:@"%@%@.json.gz", kFastSearchURI, query]];
  RKRequest* request = [[RKRequest alloc] initWithURL:url delegate:self];
  searchingIndicatorView_.hidden = NO;
  [[RKClient sharedClient].requestQueue addRequest:request];
  self.currentRequest = request;
  [request release];
}

- (void)sendSearchRequest {
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
  objectLoader.params = params;
  searchingIndicatorView_.hidden = NO;
  [objectLoader send];
  self.currentRequest = objectLoader;
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
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
    self.currentResultType = ResultTypeFast;
    self.resultsArray = array;
    [self.tableView reloadData];
  } else if (response.isNotFound) {
    self.resultsArray = nil;
    [self.tableView reloadData];
  }
  searchingIndicatorView_.hidden = YES;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  searchingIndicatorView_.hidden = YES;
  self.currentResultType = ResultTypeFull;
  self.resultsArray = objects;
  [self.tableView reloadData];
  self.currentRequest = nil;
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
  } else if ([objectLoader.response isNotFound]) {
    self.currentRequest = nil;
    [self sendSearchRequest];
    return;
  }
  searchingIndicatorView_.hidden = YES;
  [searchField_ becomeFirstResponder];
  self.currentRequest = nil;
}

#pragma mark - UITableViewDelegate Methods.

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  if (!resultsArray_)
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
  view.leftLabel.text = self.currentResultType == ResultTypeFull ? @"All results" : @"Popular results";
  return view;
}

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  SearchResult* result = nil;
  if (indexPath.row == [resultsArray_ count]) {
    result = [[[SearchResult alloc] init] autorelease];
    result.title = self.searchField.text;
  } else {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row];
  }
  
  CreateStampViewController* detailViewController =
      [[CreateStampViewController alloc] initWithSearchResult:result];
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
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
    searchingIndicatorView_.hidden = YES;
  }
}

@end
