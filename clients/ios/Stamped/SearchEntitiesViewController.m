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
#import "STNoResultsTableViewCell.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"
#import "Util.h"

static NSString* const kNearbyPath = @"/entities/nearby.json";
static NSString* const kSearchPath = @"/entities/search.json";
static NSString* const kFastSearchURI = @"http://static.stamped.com/search/v2/";

// This MUST be kept in sync with the enum order of StampFilterType.

NSString* const kSearchFilterStrings[6] = {
  @"",
  @"food",
  @"book",
  @"music",
  @"film",
  @"other"
};

typedef enum {
  ResultTypeFast,
  ResultTypeFull,
  ResultTypeLocal
} ResultType;


@interface SearchEntitiesViewController ()
- (void)createFilterBar;
- (void)textFieldDidChange:(id)sender;
- (void)sendSearchRequest;
- (void)sendFastSearchRequest;
- (void)sendSearchNearbyRequest;
- (void)reloadTableData;

@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, copy) NSArray* cachedAutocompleteResults;
@property (nonatomic, retain) CLLocationManager* locationManager;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@property (nonatomic, retain) RKRequest* currentRequest;
@property (nonatomic, assign) ResultType currentResultType;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, readonly) UIButton* clearFilterButton;
@property (nonatomic, assign) StampFilterType currentSearchFilter;
@property (nonatomic, retain) UIImageView* notConnectedImageView;
@property (nonatomic, retain) STStampFilterBar* stampFilterBar;
@end

@implementation SearchEntitiesViewController

@synthesize resultsArray = resultsArray_;
@synthesize cachedAutocompleteResults = cachedAutocompleteResults_;
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
@synthesize nearbyImageView = nearbyImageView_;
@synthesize searchButton = searchButton_;
@synthesize notConnectedImageView = notConnectedImageView_;
@synthesize stampFilterBar = stampFilterBar_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.resultsArray = nil;
  self.cachedAutocompleteResults = nil;
  self.searchField = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  self.searchingIndicatorCell = nil;
  self.currentRequest = nil;
  self.locationButton = nil;
  self.loadingIndicatorLabel = nil;
  self.tableView = nil;
  self.nearbyImageView = nil;
  self.searchButton = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
  self.notConnectedImageView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Search"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
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
  stampFilterBar_ = [[STStampFilterBar alloc] initWithFrame:CGRectMake(0, 0, 320, 44)
                                                      style:STStampFilterBarStyleDark];
  stampFilterBar_.delegate = self;
  
  UIImageView* iv = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_notConnected"]];
  CGFloat xOffset = CGRectGetWidth(self.view.bounds) - CGRectGetWidth(iv.bounds);
  iv.frame = CGRectOffset(iv.frame, floorf(xOffset / 2), 140);
  self.notConnectedImageView = iv;
  [self.view addSubview:self.notConnectedImageView];
  [iv release];

  self.notConnectedImageView.alpha = 0.0;
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    self.notConnectedImageView.alpha = 1.0;
}

- (void)createFilterBar {
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
  self.nearbyImageView = nil;
  self.searchButton = nil;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  tooltipImageView_ = nil;
  clearFilterButton_ = nil;
  self.notConnectedImageView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow animated:animated];

  [self.navigationController setNavigationBarHidden:YES animated:animated];

  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable) {
    self.notConnectedImageView.alpha = 0.0;
  } else {
    [self resetState];
    self.notConnectedImageView.alpha = 1.0;
  }

  switch (self.searchIntent) {
    case SearchIntentStamp:
      searchField_.placeholder = locationButton_.selected ? @"Search nearby" : @"Find something to stamp";
      break;
    case SearchIntentTodo:
      self.searchField.placeholder = @"Find something to do";
      break;
    default:
      break;
  }
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self.locationManager startUpdatingLocation];
  RKClient* client = [RKClient sharedClient];
  if (self.searchField.text.length == 0 && currentResultType_ != ResultTypeLocal &&
      client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable) {
    [UIView animateWithDuration:0.3 animations:^{
      tooltipImageView_.alpha = 1.0;
    }];
    [searchField_ becomeFirstResponder];
  }
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  if (self.searchField.text.length == 0)
    tooltipImageView_.alpha = 0.0;

  if (self.navigationController.viewControllers.count > 1)
    [self.navigationController setNavigationBarHidden:NO animated:animated];

  [self.locationManager stopUpdatingLocation];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)searchButtonPressed:(id)sender {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    return;
  currentResultType_ = ResultTypeFast;
  searchField_.enabled = YES;
  self.currentSearchFilter = StampFilterTypeNone;
  self.cachedAutocompleteResults = nil;
  self.resultsArray = nil;
  [self reloadTableData];
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  self.searchField.text = nil;
  [self stampFilterBar:stampFilterBar_ didSelectFilter:StampFilterTypeNone andQuery:nil];
  searchField_.placeholder = @"Find something to stamp";
  CGRect searchFrame = searchField_.frame;
  searchFrame.size.width = 207;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     searchButton_.alpha = 0;
                     searchField_.frame = searchFrame;
                     searchField_.alpha = 1;
                     locationButton_.frame = CGRectOffset(locationButton_.frame, 115, 0);
                     locationButton_.alpha = 1;
                     nearbyImageView_.frame = CGRectOffset(nearbyImageView_.frame, 118, 0);
                     nearbyImageView_.alpha = 0;
                     tooltipImageView_.alpha = 1;
                   }
                   completion:nil];
  [searchField_ becomeFirstResponder];
}

- (IBAction)locationButtonPressed:(id)sender {
  if ([[CLLocationManager class] respondsToSelector:@selector(authorizationStatus)] &&
      [CLLocationManager authorizationStatus] != kCLAuthorizationStatusAuthorized) {
    UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:nil
                                                     message:@"Location services aren't available to Stamped. You can enable them within the Settings app."
                                                    delegate:nil
                                           cancelButtonTitle:nil
                                           otherButtonTitles:@"OK", nil] autorelease];
    [alert show];
    return;
  }
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    return;
  self.currentResultType = ResultTypeLocal;
  self.currentSearchFilter = StampFilterTypeNone;
  self.resultsArray = nil;
  [self reloadTableData];
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  self.searchField.text = nil;
  [self stampFilterBar:stampFilterBar_ didSelectFilter:StampFilterTypeNone andQuery:nil];
  [searchField_ resignFirstResponder];
  searchField_.enabled = NO;
  searchField_.placeholder = nil;

  [self sendSearchNearbyRequest];

  CGRect searchFrame = searchField_.frame;
  searchFrame.size.width = 34;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     searchButton_.alpha = 1;
                     nearbyImageView_.alpha = 1;
                     searchField_.frame = searchFrame;
                     searchField_.alpha = 0;
                     locationButton_.frame = CGRectOffset(locationButton_.frame, -115, 0);
                     locationButton_.alpha = 0;
                     nearbyImageView_.frame = CGRectOffset(nearbyImageView_.frame, -118, 0);
                     tooltipImageView_.alpha = 0;
                   }
                   completion:nil];
}

- (IBAction)cancelButtonPressed:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

- (void)reloadTableData {
  [self.tableView reloadData];
  if (currentResultType_ != ResultTypeFull || [tableView_ numberOfRowsInSection:0] == 0)
    tableView_.tableHeaderView = nil;
  else
    tableView_.tableHeaderView = stampFilterBar_;
  tableView_.hidden = [tableView_ numberOfRowsInSection:0] == 0;
}

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query {
  self.resultsArray = nil;
  self.cachedAutocompleteResults = nil;
  [self reloadTableData];
  
  currentSearchFilter_ = filterType;
  
  if (searchField_.text.length)
    [self sendSearchRequest];
}

- (void)stampFilterBarSearchFieldDidBeginEditing {
  // Do nothing. TODO(andybons): Make optional.
}

- (void)stampFilterBarSearchFieldDidEndEditing {
  // Do nothing.
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if ((currentResultType_ == ResultTypeFast || (currentResultType_ == ResultTypeLocal && !loading_)) ||
      (currentResultType_ == ResultTypeFull && searchIntent_ == SearchIntentTodo && !loading_ && resultsArray_.count > 0)) {
    return [resultsArray_ count];
  }
    
  return [resultsArray_ count] + 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (currentResultType_ == ResultTypeFast) {
    static NSString* CellIdentifier = @"AutoSuggestCell";
    SearchEntitiesAutoSuggestCell* cell =
        (SearchEntitiesAutoSuggestCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
      cell = [[[SearchEntitiesAutoSuggestCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

    SearchResult* result = [resultsArray_ objectAtIndex:indexPath.row];
    cell.customTextLabel.text = result.title;
    return cell;
  }

  if (indexPath.row == [resultsArray_ count] && currentResultType_ == ResultTypeFull && !loading_) {
    if (searchIntent_ == SearchIntentStamp)
      return self.addStampCell;
    else if (searchIntent_ == SearchIntentTodo && resultsArray_.count == 0)
      return [STNoResultsTableViewCell cell];
  }
  
  if (indexPath.row == [resultsArray_ count] && currentResultType_ != ResultTypeFast && loading_)
    return self.searchingIndicatorCell;
  
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

  self.cachedAutocompleteResults = nil;
  self.resultsArray = nil;
  [self sendSearchRequest];
  [searchField_ resignFirstResponder];
  return NO;
}

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.currentRequest = nil;
  self.currentResultType = ResultTypeFast;
  self.cachedAutocompleteResults = nil;
  self.resultsArray = nil;
  [self reloadTableData];
  return YES;
}

- (void)sendFastSearchRequest {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    return;

  self.currentResultType = ResultTypeFast;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  NSString* query = self.searchField.text;
  query = [query lowercaseString];
  query = [query stringByReplacingOccurrencesOfString:@" " withString:@"_"];
  NSString* URLString = [NSString stringWithFormat:@"%@%@.json.gz", kFastSearchURI, query];
  if (currentSearchFilter_ != StampFilterTypeNone) {
    NSString* queryString = [NSString stringWithFormat:@"?category=%@", kSearchFilterStrings[currentSearchFilter_]];
    URLString = [URLString stringByAppendingString:queryString];
  }
  NSURL* url = [NSURL URLWithString:URLString];
  RKRequest* request = [[RKRequest alloc] initWithURL:url delegate:self];
  request.URLRequest.timeoutInterval = 3;
  [[RKClient sharedClient].requestQueue addRequest:request];
  self.currentRequest = request;
  [request release];
}

- (void)sendSearchRequest {
  RKClient* client = [RKClient sharedClient];
  self.cachedAutocompleteResults = nil;
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    self.resultsArray = nil;
    [self reloadTableData];
    if (notConnectedImageView_.alpha < 0.1)
      [UIView animateWithDuration:0.33 animations:^{self.notConnectedImageView.alpha = 1.0;}];
    return;
  }
  if (notConnectedImageView_.alpha > 0.9)
    [UIView animateWithDuration:0.33 animations:^{self.notConnectedImageView.alpha = 0.0;}];
  
  [searchField_ resignFirstResponder];
  currentResultType_ = ResultTypeFull;
  switch (currentSearchFilter_) {
    case StampFilterTypeBook:
      loadingIndicatorLabel_.text = @"Searching books...";
      break;
    case StampFilterTypeFood:
      loadingIndicatorLabel_.text = @"Searching restaurants & bars...";
      break;
    case StampFilterTypeMusic:
      loadingIndicatorLabel_.text = @"Searching music...";
      break;
    case StampFilterTypeFilm:
      loadingIndicatorLabel_.text = @"Searching movies & TV shows...";
      break;
    case StampFilterTypeOther:
    case StampFilterTypeNone:
    default:
      loadingIndicatorLabel_.text = @"Searching...";
      break;
  }

  self.loading = YES;
  [self reloadTableData];

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

  if (currentSearchFilter_ != StampFilterTypeNone)
    [params setObject:kSearchFilterStrings[currentSearchFilter_] forKey:@"category"];

  objectLoader.params = params;
  [objectLoader send];
  self.currentRequest = objectLoader;
}

- (void)sendSearchNearbyRequest {
  currentResultType_ = ResultTypeLocal;
  loadingIndicatorLabel_.text = @"Loading popular results nearby";
  self.loading = YES;
  self.resultsArray = nil;
  [self reloadTableData];
  
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* searchResultMapping = [objectManager.mappingProvider mappingForKeyPath:@"SearchResult"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kNearbyPath delegate:self];
  objectLoader.objectMapping = searchResultMapping;

  // TODO(error): Error message for the case where location is not turned on.
  NSMutableDictionary* params = [NSMutableDictionary dictionary];
  if (self.locationManager.location) {
    CLLocationCoordinate2D coordinate = self.locationManager.location.coordinate;
    NSString* coordString = [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
    [params setObject:coordString forKey:@"coordinates"];
  }

  objectLoader.params = params;
  [objectLoader send];
  self.currentRequest = objectLoader;
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
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
    NSMutableArray* terms = [NSMutableArray array];
    for (NSUInteger i = 0; i < MIN(10, [body count]); ++i) {
      id object = [body objectAtIndex:i];
      SearchResult* result = [[[SearchResult alloc] init] autorelease];
      result.title = [object valueForKey:@"title"];
      result.category = [object valueForKey:@"category"];
      result.subtitle = [object valueForKey:@"subtitle"];
      result.searchID = [object valueForKey:@"search_id"];
      result.entityID = [object valueForKey:@"entity_id"];
      if (![terms containsObject:result.title]) {
        [array addObject:result];
        [terms addObject:result.title];
      }
    }
    if (currentSearchFilter_ != StampFilterTypeNone) {
      NSPredicate* predicate = [NSPredicate predicateWithFormat:@"category == %@",
          kSearchFilterStrings[currentSearchFilter_]];
      self.resultsArray = [array filteredArrayUsingPredicate:predicate];
    } else {
      self.resultsArray = array;
    }
    self.cachedAutocompleteResults = self.resultsArray;
    [self reloadTableData];
  } else if (response.statusCode >= 400 && response.statusCode < 500) {
    NSPredicate* predicate = [NSPredicate predicateWithFormat:@"title CONTAINS[cd] %@", self.searchField.text];
    self.resultsArray = [self.cachedAutocompleteResults filteredArrayUsingPredicate:predicate];
    [self reloadTableData];
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  if ([request.URL.absoluteString rangeOfString:kFastSearchURI].location == NSNotFound)
    return;

  NSPredicate* predicate = [NSPredicate predicateWithFormat:@"title CONTAINS[cd] %@", self.searchField.text];
  self.resultsArray = [self.cachedAutocompleteResults filteredArrayUsingPredicate:predicate];
  [self reloadTableData];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  self.loading = NO;
  NSMutableArray* results = [NSMutableArray arrayWithArray:objects];
  for (SearchResult* result in resultsArray_) {
    NSString* entityID = result.searchID.length > 0 ? result.searchID : result.entityID;
    for (SearchResult* newResult in objects) {
      if ([newResult.searchID isEqualToString:entityID] || [newResult.entityID isEqualToString:entityID])
        [results removeObject:newResult];
    }
  }
  if (self.resultsArray)
    self.resultsArray = [self.resultsArray arrayByAddingObjectsFromArray:results];
  else
    self.resultsArray = objects;

  [self reloadTableData];
  self.currentRequest = nil;
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  self.loading = NO;
  self.currentRequest = nil;
  self.resultsArray = nil;
  [self reloadTableData];
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    return;
  }
  if (currentResultType_ == ResultTypeLocal) {
    // TODO(error)
  } else {
    [searchField_ becomeFirstResponder];
  }
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
      [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.69 alpha:0.9].CGColor,
                                (id)[UIColor colorWithWhite:0.75 alpha:0.9].CGColor, nil];
  id layerToReplace = nil;
  for (CALayer* layer in view.layer.sublayers) {
    if ([layer isKindOfClass:[CAGradientLayer class]]) {
      layerToReplace = layer;
      break;
    }
  }
      
  if (layerToReplace)
    [view.layer replaceSublayer:layerToReplace with:gradientLayer];
  else
    [view.layer insertSublayer:gradientLayer below:view.leftLabel.layer];
  [gradientLayer release];
  if (currentSearchFilter_ == StampFilterTypeNone ||
      currentSearchFilter_ == StampFilterTypeFood ||
      currentSearchFilter_ == StampFilterTypeOther ||
      currentResultType_ == ResultTypeLocal) {
    UIImageView* google = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"poweredbygoogle"]];
    google.frame = CGRectOffset(google.frame, 213, 5);
    [view addSubview:google];
    [google release];
  }
  view.leftLabel.textColor = view.leftLabel.shadowColor;
  view.leftLabel.shadowColor = [UIColor stampedGrayColor];
  view.leftLabel.shadowOffset = CGSizeMake(0, -1);
  if (resultsArray_ && resultsArray_.count == 0) {
    view.leftLabel.text = @"No results";
  } else if (currentResultType_ == ResultTypeLocal) {
    view.leftLabel.text = @"Popular nearby";
  } else {
    NSString* corpus = @"All results";
    switch (currentSearchFilter_) {
      case StampFilterTypeBook:
        corpus = @"Books only";
        break;
      case StampFilterTypeMusic:
        corpus = @"Music only";
        break;
      case StampFilterTypeFilm:
        corpus = @"Movies & TV shows only";
        break;
      case StampFilterTypeFood:
        corpus = @"Restaurants & bars only";
        break;
      case StampFilterTypeOther:
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
    SearchResult* result = [resultsArray_ objectAtIndex:indexPath.row];
    self.searchField.text = result.title;
    self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
    self.resultsArray = [NSArray arrayWithObject:result];
    [self sendSearchRequest];
    return;
  }
  
  SearchResult* result = nil;
  BOOL fullOrLocal = (currentResultType_ == ResultTypeFull || currentResultType_ == ResultTypeLocal);
  BOOL lastCell = indexPath.row == resultsArray_.count;
  if (currentResultType_ == ResultTypeFast || (fullOrLocal && !lastCell)) {
    result = (SearchResult*)[resultsArray_ objectAtIndex:indexPath.row];
  } else if (!loading_ && lastCell && currentResultType_ == ResultTypeFull) {
    if (searchIntent_ == SearchIntentStamp) {
      result = [[[SearchResult alloc] init] autorelease];
      result.title = self.searchField.text.capitalizedString;
    } else {
      return;
    }
  } else if (loading_ && lastCell && fullOrLocal) {
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
      [detailViewController hideMainToolbar];
      [detailViewController addTodoToolbar];
      [self.navigationController pushViewController:detailViewController animated:YES];
      break;
    }
    default:
      break;
  }
}

- (void)resetState {
  self.currentResultType = ResultTypeFast;
  self.currentSearchFilter = StampFilterTypeNone;
  [[RKClient sharedClient].requestQueue cancelRequest:self.currentRequest];
  self.loading = NO;
  self.currentRequest = nil;
  self.searchField.text = nil;
  self.searchField.enabled = YES;
  self.locationButton.selected = NO;
  [self textFieldDidChange:self.searchField];
  [stampFilterBar_ reset];
  [self stampFilterBar:stampFilterBar_ didSelectFilter:StampFilterTypeNone andQuery:nil];

  CGRect frame = searchField_.frame;
  frame.size.width = 207;
  searchField_.frame = frame;
  searchButton_.alpha = 0;
  searchField_.alpha = 1;
  searchField_.placeholder = @"Find something to stamp";
  frame = locationButton_.frame;
  frame.origin.x = 217;
  locationButton_.frame = frame;
  locationButton_.alpha = 1;
  frame = nearbyImageView_.frame;
  frame.origin.x = 225;
  nearbyImageView_.frame = frame;
  nearbyImageView_.alpha = 0;
}

- (void)textFieldDidChange:(id)sender {
  if (sender != self.searchField)
    return;
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable) {
    [UIView animateWithDuration:0.3
                          delay:0
                        options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       tooltipImageView_.alpha = self.searchField.text.length > 0 ? 0.0 : 1.0;
                     }
                     completion:nil];
  }
  self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
  if (searchField_.text.length > 0) {
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
