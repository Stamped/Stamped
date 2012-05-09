//
//  STMapViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLegacyMapViewController.h"

#import "AccountManager.h"
#import "Entity.h"
#import "Favorite.h"
#import "Stamp.h"
#import "STClosableOverlayView.h"
#import "STMapIndicatorView.h"
#import "STPlaceAnnotation.h"
#import "STSearchField.h"

#import "STToolbar.h"
#import "UserImageView.h"
#import "User.h"
#import "Util.h"
#import "STStampedActions.h"

static const CGFloat kMapUserImageSize = 32.0;
static const CGFloat kMapSpanHysteresisPercentage = 0.3;
static NSString* const kInboxPath = @"/collections/inbox.json";
static NSString* const kUserPath = @"/collections/user.json";
static NSString* const kFavoritesPath = @"/favorites/show.json";
static NSString* const kFriendsPath = @"/collections/friends.json";
static NSString* const kSuggestedPath = @"/collections/suggested.json";

@interface STLegacyMapViewController ()
- (void)mapDisclosureTapped:(id)sender;
- (void)overlayTapped:(UIGestureRecognizer*)recognizer;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)addAnnotationForStamp:(Stamp*)stamp;
- (void)loadDataFromNetwork;
- (void)loadDataFromDataStore;
- (void)addAllAnnotations;
- (void)removeAllAnnotations;
- (void)zoomToCurrentLocation;
- (void)centerOnCurrentLocation;
- (void)resetCaches;
- (void)showNoLocationAlert;
- (NSString*)viewportAsString;

@property (nonatomic, retain) id<MKAnnotation> selectedAnnotation;
@property (nonatomic, assign) BOOL zoomToLocation;
@property (nonatomic, assign) MKMapRect lastMapRect;
@property (nonatomic, copy) NSArray* personalStampsArray;
@property (nonatomic, copy) NSArray* todosArray;
@property (nonatomic, copy) NSArray* userStampsCache;
@property (nonatomic, copy) NSArray* friendResultsCache;
@property (nonatomic, copy) NSArray* friendsOfFriendsResultsCache;
@property (nonatomic, copy) NSArray* popularResultsCache;
@property (nonatomic, retain) NSMutableArray* resultsArray;
@property (nonatomic, retain) NSMutableArray* cachedCoordinates;
@property (nonatomic, assign) BOOL hideToolbar;
@property (nonatomic, assign) STMapScopeSliderGranularity currentGranularity;
@property (nonatomic, readonly) STMapIndicatorView* indicatorView;
@property (nonatomic, retain) STClosableOverlayView* mapOverlayView;
@property (nonatomic, assign) BOOL alertShown;
@end

@implementation STLegacyMapViewController

@synthesize alertShown = alertShown_;
@synthesize userStampsCache = userStampsCache_;
@synthesize todosArray = todosArray_;
@synthesize personalStampsArray = personalStampsArray_;
@synthesize mapOverlayView = mapOverlayView_;
@synthesize overlayView = overlayView_;
@synthesize locationButton = locationButton_;
@synthesize cancelButton = cancelButton_;
@synthesize searchField = searchField_;
@synthesize mapView = mapView_;
@synthesize zoomToLocation = zoomToLocation_;
@synthesize scopeSlider = scopeSlider_;
@synthesize source = source_;
@synthesize user = user_;
@synthesize resultsArray = resultsArray_;
@synthesize selectedAnnotation = selectedAnnotation_;
@synthesize lastMapRect = lastMapRect_;
@synthesize toolbar = toolbar_;
@synthesize hideToolbar = hideToolbar_;
@synthesize indicatorView = indicatorView_;
@synthesize cachedCoordinates = cachedCoordinates_;
@synthesize currentGranularity = currentGranularity_;
@synthesize friendResultsCache = friendResultsCache_;
@synthesize popularResultsCache = popularResultsCache_;
@synthesize friendsOfFriendsResultsCache = friendsOfFriendsResultsCache_;

- (id)init {
  self = [super initWithNibName:@"STMapViewController" bundle:nil];
  if (self) {}
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  self.user = nil;
  self.scopeSlider.delegate = nil;
  self.scopeSlider = nil;
  self.resultsArray = nil;
  self.selectedAnnotation = nil;
  self.toolbar = nil;
  self.cachedCoordinates = nil;
  indicatorView_ = nil;
  self.mapOverlayView = nil;
  self.personalStampsArray = nil;
  self.todosArray = nil;
  self.friendResultsCache = nil;
  self.popularResultsCache = nil;
  self.friendsOfFriendsResultsCache = nil;
  self.userStampsCache = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  searchField_.placeholder = NSLocalizedString(@"Try \u201cpizza\u201d or \u201cbar\u201d", nil);
  
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(overlayTapped:)];
  [overlayView_ addGestureRecognizer:recognizer];
  [recognizer release];
  
  zoomToLocation_ = YES;
  toolbar_.hidden = hideToolbar_;
  CGRect frame = mapView_.frame;
  frame.size.height = toolbar_.hidden ? 372 : 323;
  mapView_.frame = frame;
  
  indicatorView_ = [[STMapIndicatorView alloc] init];
  indicatorView_.frame = CGRectOffset(indicatorView_.frame, 1, CGRectGetMinY(mapView_.frame) + 4);
  [self.view insertSubview:indicatorView_ belowSubview:overlayView_];
  [indicatorView_ release];
  
  self.currentGranularity = scopeSlider_.granularity;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  self.scopeSlider.delegate = nil;
  self.scopeSlider = nil;
  self.selectedAnnotation = nil;
  self.toolbar = nil;
  indicatorView_ = nil;
  self.mapOverlayView = nil;
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  mapView_.showsUserLocation = NO;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  toolbar_.hidden = hideToolbar_;
  CGRect frame = mapView_.frame;
  frame.size.height = toolbar_.hidden ? 372 : 323;
  mapView_.frame = frame;
  [mapView_ setNeedsDisplay];
  if (mapView_.selectedAnnotations.count == 0)
    [self loadDataFromNetwork];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  
  if (mapOverlayView_)
    return;
  
  if ([[NSUserDefaults standardUserDefaults] boolForKey:@"hasSeenNewMapsView"]) {
    if ([[CLLocationManager class] respondsToSelector:@selector(authorizationStatus)] &&
        [CLLocationManager authorizationStatus] != kCLAuthorizationStatusAuthorized &&
        !alertShown_) {
      [self showNoLocationAlert];
    }
    mapView_.showsUserLocation = YES;
    if (mapView_.selectedAnnotations.count == 0 && !hideToolbar_)
      [scopeSlider_ flashTooltip];
  } else {
    self.mapOverlayView = [[[STClosableOverlayView alloc] init] autorelease];
    UIImageView* content = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_maps_welcome"]];
    [mapOverlayView_.contentView addSubview:content];
    [content release];
    [mapOverlayView_ showWithOnCloseHandler:^{
      [self performSelectorOnMainThread:@selector(setMapOverlayView:) withObject:nil waitUntilDone:NO];
      [mapView_ performSelectorOnMainThread:@selector(setShowsUserLocation:)
                                 withObject:[NSNumber numberWithBool:YES]
                              waitUntilDone:NO];
      if (mapView_.selectedAnnotations.count == 0 && !hideToolbar_)
        [scopeSlider_ performSelectorOnMainThread:@selector(flashTooltip) withObject:nil waitUntilDone:NO];
    }];
    
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"hasSeenNewMapsView"];
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"hideMapButtonTooltip"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (UINavigationController*)navigationController {
  if ([super navigationController])
    return [super navigationController];
  
  return [Util sharedNavigationController];
}

- (void)setSource:(STMapViewControllerSource)source {
  if (source != source_) {
    source_ = source;
  }
  
  hideToolbar_ = (source_ != STMapViewControllerSourceInbox);
  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    if (source_ == STMapViewControllerSourceInbox)
      [scopeSlider_ setGranularity:STMapScopeSliderGranularityFriends animated:NO];
    else if (source_ == STMapViewControllerSourceUser)
      [scopeSlider_ setGranularity:STMapScopeSliderGranularityYou animated:NO];
  }
  [self removeAllAnnotations];
}

#pragma mark - UITextFieldDelegate methods.

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  CGFloat offset = (CGRectGetWidth(cancelButton_.frame) + 5) * -1;
  cancelButton_.alpha = 1;
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  indicatorView_.mode = STMapIndicatorViewModeHidden;
  [UIView animateWithDuration:0.2 animations:^{
    locationButton_.frame = CGRectOffset(locationButton_.frame, offset, 0);
    cancelButton_.frame = CGRectOffset(cancelButton_.frame, offset, 0);
    CGRect frame = searchField_.frame;
    frame.size.width += offset;
    searchField_.frame = frame;
    overlayView_.alpha = 0.75;
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:NO animated:YES];
  CGFloat offset = CGRectGetWidth(cancelButton_.frame) + 5;
  [UIView animateWithDuration:0.2 animations:^{
    locationButton_.frame = CGRectOffset(locationButton_.frame, offset, 0);
    cancelButton_.frame = CGRectOffset(cancelButton_.frame, offset, 0);
    CGRect frame = searchField_.frame;
    frame.size.width += offset;
    searchField_.frame = frame;
    overlayView_.alpha = 0;
  } completion:^(BOOL finished) {
    cancelButton_.alpha = 0;
  }];
  [self loadDataFromNetwork];
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  [searchField_ resignFirstResponder];
}

- (IBAction)locationButtonPressed:(id)sender {
  if ([[CLLocationManager class] respondsToSelector:@selector(authorizationStatus)] &&
      [CLLocationManager authorizationStatus] != kCLAuthorizationStatusAuthorized) {
    [self showNoLocationAlert];
    return;
  }
  [self centerOnCurrentLocation];
}

#pragma mark - Gesture recognizers.

- (void)overlayTapped:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;
  
  [searchField_ resignFirstResponder];
}

- (void)mapUserTapped:(id)sender {
  UserImageView* userImage = sender;
  UIView* view = [userImage superview];
  while (view && ![view isMemberOfClass:[MKPinAnnotationView class]])
    view = [view superview];
  
  if (!view)
    return;
  
   STPlaceAnnotation* annotation = (STPlaceAnnotation*)[(MKPinAnnotationView*)view annotation];
  [[STStampedActions sharedInstance] viewUserWithUserID:annotation.stamp.user.userID];
}

- (void)mapDisclosureTapped:(id)sender {
  UIButton* disclosureButton = sender;
  UIView* view = [disclosureButton superview];
  while (view && ![view isMemberOfClass:[MKPinAnnotationView class]])
    view = [view superview];
  
  if (!view)
    return;
  
  STPlaceAnnotation* annotation = (STPlaceAnnotation*)[(MKPinAnnotationView*)view annotation];
  UIViewController* vc = nil;
  if (annotation.stamp) {
    [[STStampedActions sharedInstance] viewStampWithStampID:annotation.stamp.stampID];
  } else if (annotation.entityObject) {
    vc = [Util detailViewControllerForEntity:annotation.entityObject];
  }
  if (!vc)
    return;
  
  [self.navigationController pushViewController:vc animated:YES];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)loader didLoadObjects:(NSArray*)objects {
  if (!resultsArray_)
    self.resultsArray = [NSMutableArray array];
  
  for (id obj in objects) {
    if ([resultsArray_ containsObject:obj])
      continue;
    [resultsArray_ addObject:obj];
  }
  if (searchField_.text.length > 0) {
    indicatorView_.mode = resultsArray_.count > 0 ? STMapIndicatorViewModeHidden : STMapIndicatorViewModeNoResults;
  } else {
    indicatorView_.mode = STMapIndicatorViewModeHidden;
  }
  
  [self addAllAnnotations];
}

- (void)objectLoader:(RKObjectLoader*)loader didFailWithError:(NSError*)error {
  if ([loader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadDataFromNetwork];
    return;
  }
  indicatorView_.mode = STMapIndicatorViewModeHidden;  // TODO(andybons): Add error mode?
  NSLog(@"Error loading map data: %@. Error code: %d", error.localizedDescription, loader.response.statusCode);
}

#pragma mark - MKMapViewDelegate Methods

- (void)mapView:(MKMapView*)mapView didUpdateUserLocation:(MKUserLocation*)userLocation {
  if (zoomToLocation_) {
    [self zoomToCurrentLocation];
    zoomToLocation_ = NO;
  }
}

- (void)mapView:(MKMapView*)mapView regionDidChangeAnimated:(BOOL)animated {
  // Calculate delta of origins across longitudinal distance.
  CGFloat originDelta = MKMetersBetweenMapPoints(lastMapRect_.origin, mapView.visibleMapRect.origin);
  MKMapPoint upperRight = MKMapPointMake(MKMapRectGetMaxX(lastMapRect_), MKMapRectGetMinY(lastMapRect_));
  CGFloat span = MKMetersBetweenMapPoints(lastMapRect_.origin, upperRight);
  
  if ((originDelta / span) < kMapSpanHysteresisPercentage)
    return;
  
  if (searchField_.text.length > 0)
    return;
  
  lastMapRect_ = mapView.visibleMapRect;
  [self resetCaches];
  [self loadDataFromNetwork];
}

- (MKAnnotationView*)mapView:(MKMapView*)theMapView viewForAnnotation:(id<MKAnnotation>)annotation {
  if (![annotation isKindOfClass:[STPlaceAnnotation class]])
    return nil;
  
  MKPinAnnotationView* pinView = [[[MKPinAnnotationView alloc] initWithAnnotation:annotation reuseIdentifier:nil] autorelease];
  UIButton* disclosureButton = [UIButton buttonWithType:UIButtonTypeDetailDisclosure];
  [disclosureButton addTarget:self
                       action:@selector(mapDisclosureTapped:)
             forControlEvents:UIControlEventTouchUpInside];
  pinView.rightCalloutAccessoryView = disclosureButton;
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.canShowCallout = YES;
  
  Stamp* stamp = [(STPlaceAnnotation*)annotation stamp];
  if (stamp) {
    UserImageView* userImageView = [[UserImageView alloc] initWithFrame:CGRectMake(0, 0, kMapUserImageSize, kMapUserImageSize)];
    userImageView.enabled = YES;
    [userImageView addTarget:self
                      action:@selector(mapUserTapped:)
            forControlEvents:UIControlEventTouchUpInside];
    if (source_ == STMapViewControllerSourceInbox)
      userImageView.imageURL = [stamp.user profileImageURLForSize:ProfileImageSize37];
    else if (source_ == STMapViewControllerSourceUser && user_)
      userImageView.imageURL = [user_ profileImageURLForSize:ProfileImageSize37];
    
    pinView.leftCalloutAccessoryView = userImageView;
    pinView.animatesDrop = searchField_.text.length > 0;
    [userImageView release];
  }
  
  return pinView;
}

#pragma mark - Other private methods.

- (void)loadDataFromDataStore {
  if (source_ == STMapViewControllerSourceUser && !userStampsCache_)
    self.userStampsCache = [Stamp objectsWithPredicate:[NSPredicate predicateWithFormat:@"deleted == NO AND user.userID == %@", user_.userID]];
  
  if (scopeSlider_.granularity == STMapScopeSliderGranularityYou && !personalStampsArray_)
    self.personalStampsArray = [Stamp objectsWithPredicate:[NSPredicate predicateWithFormat:@"deleted == NO AND user.userID == %@", [AccountManager sharedManager].currentUser.userID]];
  
  if (source_ == STMapViewControllerSourceTodo)
    self.todosArray = [Favorite objectsWithPredicate:[NSPredicate predicateWithFormat:@"entityObject != NIL"]];
  
  [self addAllAnnotations];
}

- (void)loadDataFromNetwork {
  if (searchField_.text.length == 0) {
    if ((scopeSlider_.granularity == STMapScopeSliderGranularityYou || source_ == STMapViewControllerSourceTodo || source_ == STMapViewControllerSourceUser) ||
        (scopeSlider_.granularity == STMapScopeSliderGranularityFriends && friendResultsCache_) ||
        (scopeSlider_.granularity == STMapScopeSliderGranularityFriendsOfFriends && friendsOfFriendsResultsCache_) ||
        (scopeSlider_.granularity == STMapScopeSliderGranularityEveryone && popularResultsCache_)) {
      [self loadDataFromDataStore];
      return;
    }
  }
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    indicatorView_.mode = STMapIndicatorViewModeNoConnection;
    return;
  }
  
  indicatorView_.mode = STMapIndicatorViewModeLoading;
  
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  NSString* keyPath = source_ == STMapViewControllerSourceTodo ? @"Favorite" : @"Stamp";
  RKObjectMapping* mapping = [objectManager.mappingProvider mappingForKeyPath:keyPath];
  NSString* path = nil;
  switch (scopeSlider_.granularity) {
    case STMapScopeSliderGranularityYou:
      path = kUserPath;
      break;
    case STMapScopeSliderGranularityFriends:
      path = kInboxPath;
      break;
    case STMapScopeSliderGranularityFriendsOfFriends:
      path = kFriendsPath;
      break;
    case STMapScopeSliderGranularityEveryone:
      path = kSuggestedPath;
      break;
    default:
      break;
  }
  
  if (source_ == STMapViewControllerSourceTodo)
    path = kFavoritesPath;
  
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.objectMapping = mapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:@"1", @"quality",
                                 [self viewportAsString], @"viewport", @"relevance", @"sort", @"true", @"unique", nil];
  if (searchField_.text.length > 0) {
    [self removeAllAnnotations];
    self.resultsArray = nil;
    self.cachedCoordinates = nil;
    [params setValue:searchField_.text forKey:@"query"];
  }
  
  if (scopeSlider_.granularity == STMapScopeSliderGranularityYou) {
    if (source_ == STMapViewControllerSourceInbox) {
      [params setValue:[AccountManager sharedManager].currentUser.screenName forKey:@"screen_name"];
    } else if (source_ == STMapViewControllerSourceUser) {
      [params setValue:user_.screenName forKey:@"screen_name"];
    }
  } else if (scopeSlider_.granularity == STMapScopeSliderGranularityFriendsOfFriends) {
    [params setValue:@"false" forKey:@"inclusive"];
  }
  
  objectLoader.params = params;
  [objectLoader send];
}

- (void)addAllAnnotations {
  self.selectedAnnotation = nil;
  
  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    NSArray* stamps = nil;
    if (searchField_.text.length > 0) {
      stamps = resultsArray_;
    } else if (source_ == STMapViewControllerSourceUser) {
      stamps = userStampsCache_;
    } else if (scopeSlider_.granularity == STMapScopeSliderGranularityYou) {
      stamps = personalStampsArray_;
    } else if (scopeSlider_.granularity == STMapScopeSliderGranularityFriends) {
      if (!friendResultsCache_)
        self.friendResultsCache = [NSArray arrayWithArray:resultsArray_];
      
      stamps = friendResultsCache_;      
    } else if (scopeSlider_.granularity == STMapScopeSliderGranularityFriendsOfFriends) {
      if (!friendsOfFriendsResultsCache_)
        self.friendsOfFriendsResultsCache = [NSArray arrayWithArray:resultsArray_];
      
      stamps = friendsOfFriendsResultsCache_;
    } else if (scopeSlider_.granularity == STMapScopeSliderGranularityEveryone) {
      if (!popularResultsCache_)
        self.popularResultsCache = [NSArray arrayWithArray:resultsArray_];
      
      stamps = popularResultsCache_;
    } else {
      stamps = [NSArray arrayWithArray:resultsArray_];
    }
    
    for (Stamp* s in stamps) {
      if (s.entityObject.coordinates.length > 0)
        [self addAnnotationForStamp:s];
    }
  } else if (source_ == STMapViewControllerSourceTodo) {
    NSArray* entities = nil;
    if (searchField_.text.length > 0) {
      entities = resultsArray_;
    } else {
      entities = todosArray_;
    }
    
    for (Favorite* f in entities) {
      if (f.entityObject.coordinates.length > 0)
        [self addAnnotationForEntity:f.entityObject];
    }
  }
  
  if (selectedAnnotation_ && searchField_.text.length > 0) {
    // Search result. Let's zoom in/out to encompass all stamps with some padding...
    CLLocationCoordinate2D maxCoord = {-90.0f, -180.0f};
    CLLocationCoordinate2D minCoord = {90.0f, 180.0f};
    for (id<MKAnnotation> annotation in mapView_.annotations) {
      if (![annotation isMemberOfClass:[STPlaceAnnotation class]])
        continue;
      
      CLLocationCoordinate2D coord = annotation.coordinate;
      if (coord.longitude > maxCoord.longitude)
        maxCoord.longitude = coord.longitude;
      
      if (coord.latitude > maxCoord.latitude)
        maxCoord.latitude = coord.latitude;
      
      if (coord.longitude < minCoord.longitude)
        minCoord.longitude = coord.longitude;
      
      if (coord.latitude < minCoord.latitude)
        minCoord.latitude = coord.latitude;
    }
    MKCoordinateRegion region = {{0.0f, 0.0f}, {0.0f, 0.0f}};
    region.center.longitude = (minCoord.longitude + maxCoord.longitude) / 2.0;
    region.center.latitude = (minCoord.latitude + maxCoord.latitude) / 2.0;
    region.span.longitudeDelta = maxCoord.longitude - minCoord.longitude;
    region.span.latitudeDelta = maxCoord.latitude - minCoord.latitude;
    [mapView_ setRegion:region animated:YES];
    [mapView_ selectAnnotation:selectedAnnotation_ animated:YES];
  }
}

- (void)removeAllAnnotations {
  NSMutableArray* toRemove = [NSMutableArray arrayWithCapacity:mapView_.annotations.count];
  for (id<MKAnnotation> annotation in mapView_.annotations) {
    if ([annotation isMemberOfClass:[STPlaceAnnotation class]])
      [toRemove addObject:annotation];
  }
  
  for (STPlaceAnnotation* annotation in toRemove)
    [mapView_ removeAnnotation:annotation];
  
  self.cachedCoordinates = nil;
}

- (void)addAnnotationForEntity:(Entity*)entity {
  if (!cachedCoordinates_)
    self.cachedCoordinates = [NSMutableArray array];
  
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
  if ([cachedCoordinates_ containsObject:coordinates])
    return;
  
  [cachedCoordinates_ addObject:coordinates];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];
  
  annotation.entityObject = entity;
  [mapView_ addAnnotation:annotation];
  [annotation release];
  if (!selectedAnnotation_)
    self.selectedAnnotation = annotation;
}

- (void)addAnnotationForStamp:(Stamp*)stamp {
  if (!cachedCoordinates_)
    self.cachedCoordinates = [NSMutableArray array];
  
  NSArray* coordinates = [stamp.entityObject.coordinates componentsSeparatedByString:@","];
  if ([cachedCoordinates_ containsObject:coordinates])
    return;
  
  [cachedCoordinates_ addObject:coordinates];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];
  annotation.stamp = stamp;
  [mapView_ addAnnotation:annotation];
  [annotation release];
  if (!selectedAnnotation_)
    self.selectedAnnotation = annotation;
}

- (void)zoomToCurrentLocation {
  CLLocationCoordinate2D currentLocation = mapView_.userLocation.location.coordinate;
  MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kStandardLatLongSpan, kStandardLatLongSpan);
  MKCoordinateRegion region = MKCoordinateRegionMake(currentLocation, mapSpan);
  [mapView_ setRegion:region animated:YES];
}

- (void)centerOnCurrentLocation {
  [mapView_ setCenterCoordinate:mapView_.userLocation.location.coordinate animated:YES];
}

- (NSString*)viewportAsString {
  MKMapRect region = self.mapView.visibleMapRect;
  CLLocationCoordinate2D topLeft = MKCoordinateForMapPoint(region.origin);
  CLLocationCoordinate2D bottomRight = MKCoordinateForMapPoint(MKMapPointMake(MKMapRectGetMaxX(region), MKMapRectGetMaxY(region)));
  return [NSString stringWithFormat:@"%f,%f,%f,%f", topLeft.latitude, topLeft.longitude, bottomRight.latitude, bottomRight.longitude];
}

- (void)reset {
  self.resultsArray = nil;
  self.cachedCoordinates = nil;
  self.searchField.text = nil;
  self.selectedAnnotation = nil;
  [self resetCaches];
  [self removeAllAnnotations];
  zoomToLocation_ = YES;
  lastMapRect_ = MKMapRectNull;
}

- (void)resetCaches {
  self.userStampsCache = nil;
  self.friendResultsCache = nil;
  self.popularResultsCache = nil;
  self.friendsOfFriendsResultsCache = nil;
}

- (void)showNoLocationAlert {
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:nil
                                                   message:NSLocalizedString(@"Location services aren't available to Stamped. You can enable them within the Settings app.", nil)
                                                  delegate:self
                                         cancelButtonTitle:nil
                                         otherButtonTitles:NSLocalizedString(@"Dismiss", nil), NSLocalizedString(@"Settings", nil), nil] autorelease];
  [alert show];
  alertShown_ = YES;
}

#pragma mark - UIAlertViewDelegate methods.

- (void)alertView:(UIAlertView*)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex {
  alertShown_ = NO;
  if ([[alertView buttonTitleAtIndex:buttonIndex] isEqualToString:NSLocalizedString(@"Settings", nil)])
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:@"prefs:root=LOCATION_SERVICES"]];
}

#pragma mark - STMapScopeSliderDelegate methods.

/*
 TODO - modify for granularity caching
 */

- (void)mapScopeSlider:(STMapScopeSlider*)slider didChangeGranularity:(STMapScopeSliderGranularity)granularity {
  if (currentGranularity_ != granularity) {
    currentGranularity_ = granularity;
    self.resultsArray = nil;
    self.cachedCoordinates = nil;
    [self removeAllAnnotations];
    [self loadDataFromNetwork];
  }
}

@end
