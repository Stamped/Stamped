//
//  STMapViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapViewController.h"

#import "AccountManager.h"
#import "Entity.h"
#import "Favorite.h"
#import "ProfileViewController.h"
#import "Stamp.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "STMapIndicatorView.h"
#import "STPlaceAnnotation.h"
#import "STSearchField.h"

#import "STToolbar.h"
#import "UserImageView.h"
#import "User.h"
#import "Util.h"

static const CGFloat kMapUserImageSize = 32.0;
static const CGFloat kMapSpanHysteresisPercentage = 0.3;
static NSString* const kInboxPath = @"/collections/inbox.json";
static NSString* const kUserPath = @"/collections/user.json";
static NSString* const kFavoritesPath = @"/favorites/show.json";
static NSString* const kFriendsPath = @"/collections/friends.json";
static NSString* const kSuggestedPath = @"/collections/suggested.json";

@interface STMapViewController ()
- (void)mapDisclosureTapped:(id)sender;
- (void)overlayTapped:(UIGestureRecognizer*)recognizer;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)addAnnotationForStamp:(Stamp*)stamp;
- (void)loadDataFromNetwork;
- (void)addAllAnnotations;
- (void)removeAllAnnotations;
- (void)zoomToCurrentLocation;
- (void)centerOnCurrentLocation;
- (NSString*)viewportAsString;

@property (nonatomic, retain) id<MKAnnotation> selectedAnnotation;
@property (nonatomic, assign) BOOL zoomToLocation;
@property (nonatomic, assign) MKMapRect lastMapRect;
@property (nonatomic, copy) NSArray* resultsArray;
@property (nonatomic, assign) BOOL hideToolbar;
@property (nonatomic, readonly) STMapIndicatorView* indicatorView;
@end

@implementation STMapViewController

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
  indicatorView_ = nil;
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
  [self.view addSubview:indicatorView_];
  [indicatorView_ release];
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
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  mapView_.showsUserLocation = YES;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (UINavigationController*)navigationController {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  return delegate.navigationController;
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

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  textField.text = nil;
  [self loadDataFromNetwork];
  return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  [self loadDataFromNetwork];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  CGFloat offset = (CGRectGetWidth(cancelButton_.frame) + 5) * -1;
  cancelButton_.alpha = 1;
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
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  [searchField_ resignFirstResponder];
}

- (IBAction)locationButtonPressed:(id)sender {
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
  ProfileViewController* profileViewController = [[ProfileViewController alloc] init];
  profileViewController.user = annotation.stamp.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
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
    vc = [[[StampDetailViewController alloc] initWithStamp:annotation.stamp] autorelease];
  } else if (annotation.entityObject) {
    vc = [Util detailViewControllerForEntity:annotation.entityObject];
  }
  if (!vc)
    return;

  [self.navigationController pushViewController:vc animated:YES];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)loader didLoadObjects:(NSArray*)objects {
  self.resultsArray = objects;
  [self addAllAnnotations];
  indicatorView_.mode = resultsArray_.count > 0 ? STMapIndicatorViewModeHidden : STMapIndicatorViewModeNoResults;
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
  // Calculate delta of origins.
  CGFloat originDelta = MKMetersBetweenMapPoints(lastMapRect_.origin, mapView.visibleMapRect.origin);
  MKMapPoint lowerRight = MKMapPointMake(MKMapRectGetMaxX(lastMapRect_), MKMapRectGetMaxY(lastMapRect_));
  CGFloat span = MKMetersBetweenMapPoints(lastMapRect_.origin, lowerRight);

  if ((originDelta / span) < kMapSpanHysteresisPercentage)
    return;
  
  if (searchField_.text.length > 0)
    return;

  lastMapRect_ = mapView.visibleMapRect;
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
    [userImageView release];
  }

  return pinView;
}

#pragma mark - Other private methods.

- (void)loadDataFromNetwork {
  [self removeAllAnnotations];
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
  if (searchField_.text.length > 0)
    [params setValue:searchField_.text forKey:@"query"];

  if (scopeSlider_.granularity == STMapScopeSliderGranularityYou)
    [params setValue:[AccountManager sharedManager].currentUser.screenName forKey:@"screen_name"];

  objectLoader.params = params;
  [objectLoader send];
  indicatorView_.mode = STMapIndicatorViewModeLoading;
}

- (void)addAllAnnotations {
  [self removeAllAnnotations];
  self.selectedAnnotation = nil;

  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    for (Stamp* s in resultsArray_)
      [self addAnnotationForStamp:s];
  } else if (source_ == STMapViewControllerSourceTodo) {
    for (Favorite* f in resultsArray_)
      [self addAnnotationForEntity:f.entityObject];
  }

  if (selectedAnnotation_ && searchField_.text.length > 0)
    [mapView_ selectAnnotation:selectedAnnotation_ animated:YES];
}

- (void)removeAllAnnotations {
  NSMutableArray* toRemove = [NSMutableArray arrayWithCapacity:mapView_.annotations.count];
  for (id<MKAnnotation> annotation in mapView_.annotations) {
    if ([annotation isMemberOfClass:[STPlaceAnnotation class]])
      [toRemove addObject:annotation];
  }
  
  for (STPlaceAnnotation* annotation in toRemove)
    [mapView_ removeAnnotation:annotation];
}

- (void)addAnnotationForEntity:(Entity*)entity {
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
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
  NSArray* coordinates = [stamp.entityObject.coordinates componentsSeparatedByString:@","];
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

#pragma mark - STMapScopeSliderDelegate methods.

- (void)mapScopeSlider:(STMapScopeSlider*)slider didChangeGranularity:(STMapScopeSliderGranularity)granularity {
  [self loadDataFromNetwork];
}

@end
