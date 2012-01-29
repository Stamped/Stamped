//
//  STMapViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapViewController.h"

#import "Entity.h"
#import "Favorite.h"
#import "ProfileViewController.h"
#import "Stamp.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "STPlaceAnnotation.h"
#import "STSearchField.h"
#import "UserImageView.h"
#import "User.h"
#import "Util.h"

static const CGFloat kMapUserImageSize = 32.0;

@interface STMapViewController ()
- (void)mapDisclosureTapped:(id)sender;
- (void)overlayTapped:(UIGestureRecognizer*)recognizer;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)loadDataFromStore;
- (void)addAllAnnotations;
- (void)zoomToCurrentLocation;

@property (nonatomic, assign) BOOL zoomToLocation;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@end

@implementation STMapViewController

@synthesize overlayView = overlayView_;
@synthesize locationButton = locationButton_;
@synthesize cancelButton = cancelButton_;
@synthesize searchField = searchField_;
@synthesize mapView = mapView_;
@synthesize zoomToLocation = zoomToLocation_;
@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize source = source_;
@synthesize user = user_;

- (id)init {
  self = [super initWithNibName:@"STMapViewController" bundle:nil];
  if (self) {

  }
  return self;
}

- (void)dealloc {
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.user = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(overlayTapped:)];
  [overlayView_ addGestureRecognizer:recognizer];
  [recognizer release];

  [self zoomToCurrentLocation];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  mapView_.showsUserLocation = NO;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  mapView_.showsUserLocation = YES;
  zoomToLocation_ = YES;
  if (!self.fetchedResultsController)
    [self loadDataFromStore];
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

  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    searchField_.placeholder = @"Search stamps";
  } else if (source_ == STMapViewControllerSourceTodo) {
    searchField_.placeholder = @"Search to-dos";
  }
  self.fetchedResultsController = nil;
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  CGFloat offset = (CGRectGetWidth(cancelButton_.frame) + 5) * -1;
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
  }];
}

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
//  [self addAllAnnotations];
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  [searchField_ resignFirstResponder];
}

- (IBAction)locationButtonPressed:(id)sender {
  [self zoomToCurrentLocation];
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
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
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

#pragma mark - MKMapViewDelegate Methods

- (void)mapView:(MKMapView*)mapView didUpdateUserLocation:(MKUserLocation*)userLocation {
  if (zoomToLocation_) {
    [self zoomToCurrentLocation];
    zoomToLocation_ = NO;
  }
}

- (void)mapView:(MKMapView*)mapView regionDidChangeAnimated:(BOOL)animated {
  zoomToLocation_ = NO;
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

#pragma - Other private methods.

- (void)loadDataFromStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = nil;
    NSSortDescriptor* descriptor = nil;
    NSPredicate* predicate = nil;
    NSManagedObjectContext* moc = nil;
    if (source_ == STMapViewControllerSourceInbox) {
      request = [Entity fetchRequest];
      descriptor = [NSSortDescriptor sortDescriptorWithKey:@"mostRecentStampDate" ascending:NO];
      moc = [Entity managedObjectContext];
      predicate = [NSPredicate predicateWithFormat:@"coordinates != NIL AND (SUBQUERY(stamps, $s, $s.temporary == NO AND $s.deleted == NO).@count != 0)"];
    } else if (source_ == STMapViewControllerSourceTodo) {
      request = [Favorite fetchRequest];
      descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
      predicate = [NSPredicate predicateWithFormat:@"entityObject != NIL AND entityObject.coordinates != NIL"];
      moc = [Favorite managedObjectContext];
    } else if (source_ == STMapViewControllerSourceUser && user_) {
      request = [Entity fetchRequest];
      descriptor = [NSSortDescriptor sortDescriptorWithKey:@"mostRecentStampDate" ascending:NO];
      predicate = [NSPredicate predicateWithFormat:@"coordinates != NIL AND (SUBQUERY(stamps, $s, $s.user.userID == %@ AND $s.deleted == NO).@count != 0)", user_.userID];
      moc = [Entity managedObjectContext];
    } else {
      NSLog(@"No valid source was given for the map view.");
      return;
    }
    [request setPredicate:predicate];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setFetchBatchSize:20];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:moc
                                              sectionNameKeyPath:nil
                                                       cacheName:nil];
    self.fetchedResultsController = fetchedResultsController;
    fetchedResultsController.delegate = self;
    [fetchedResultsController release];
  }

  NSError* error;
  if (![self.fetchedResultsController performFetch:&error]) {
    // Update to handle the error appropriately.
    NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
    return;
  }
  [self addAllAnnotations];
}

- (void)addAllAnnotations {
  [mapView_ removeAnnotations:mapView_.annotations];
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
  NSArray* objectsArray = [sectionInfo objects];
  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    for (Entity* e in objectsArray)
      [self addAnnotationForEntity:e];
  } else if (source_ == STMapViewControllerSourceTodo) {
    for (Favorite* f in objectsArray)
      [self addAnnotationForEntity:f.entityObject];
  }
}

- (void)addAnnotationForEntity:(Entity*)entity {
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];

  if (source_ == STMapViewControllerSourceInbox || source_ == STMapViewControllerSourceUser) {
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
    NSArray* stampsArray = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    // Temporary stamps won't work for profile view.
    stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO AND deleted == NO"]];

    annotation.stamp = [stampsArray lastObject];
  } else if (source_ == STMapViewControllerSourceTodo) {
    annotation.entityObject = entity;
  }

  [mapView_ addAnnotation:annotation];
  [annotation release];
}

- (void)zoomToCurrentLocation {
  CLLocationCoordinate2D currentLocation = mapView_.userLocation.location.coordinate;
  MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kStandardLatLongSpan, kStandardLatLongSpan);
  MKCoordinateRegion region = MKCoordinateRegionMake(currentLocation, mapSpan);
  [mapView_ setRegion:region animated:YES];
}

@end
