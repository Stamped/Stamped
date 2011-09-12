//
//  InboxViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxViewController.h"

#import <CoreText/CoreText.h>
#import <MapKit/MapKit.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "UserImageView.h"
#import "Notifications.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "Stamp.h"
#import "STNavigationBar.h"
#import "STPlaceAnnotation.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kMapUserImageSize = 32.0;
static NSString* const kInboxPath = @"/collections/inbox.json";
static NSString* const kEverythingPath = @"/temp/inbox.json";

typedef enum {
  StampsListFilterTypeBook,
  StampsListFilterTypeFilm,
  StampsListFilterTypeMusic,
  StampsListFilterTypePlace,
  StampsListFilterTypeOther,
  StampsListFilterTypeAll
} StampsListFilterType;

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)filterStamps;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)mapUserTapped:(id)sender;
- (void)mapDisclosureTapped:(id)sender;

@property (nonatomic, copy) NSArray* filterButtons;
@property (nonatomic, retain) NSMutableArray* entitiesArray;
@property (nonatomic, retain) NSMutableArray* filteredEntitiesArray;
@property (nonatomic, retain) UIButton* selectedFilterButton;
@end

@implementation InboxViewController

@synthesize mapView = mapView_;
@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize filterButtons = filterButtons_;
@synthesize filterView = filterView_;
@synthesize foodFilterButton = foodFilterButton_;
@synthesize booksFilterButton = booksFilterButton_;
@synthesize filmFilterButton = filmFilterButton_;
@synthesize musicFilterButton = musicFilterButton_;
@synthesize otherFilterButton = otherFilterButton_;
@synthesize selectedFilterButton = selectedFilterButton_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.filterButtons = nil;
  self.filterView = nil;
  self.foodFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmFilterButton = nil;
  self.musicFilterButton = nil;
  self.otherFilterButton = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.selectedFilterButton = nil;
  [super dealloc];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  CGRect mapFrame = mapView_.frame;
  mapFrame.origin.y = self.tableView.contentOffset.y;
  mapView_.frame = mapFrame;
  userPannedMap_ = NO;
  self.tableView.scrollEnabled = NO;
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Entity* e in self.filteredEntitiesArray) {
                       if (!e.coordinates)
                         continue;
                      [self addAnnotationForEntity:e];
                     }
                   }];
}

- (void)listButtonWasPressed:(NSNotification*)notification {
  self.tableView.scrollEnabled = YES;
  mapView_.showsUserLocation = NO;
  [mapView_ removeAnnotations:mapView_.annotations];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 0.0; }];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(stampWasCreated:)
                                               name:kStampWasCreatedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(mapButtonWasPressed:)
                                               name:kMapViewButtonPressedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(listButtonWasPressed:)
                                               name:kListViewButtonPressedNotification
                                             object:nil];
  mapView_ = [[MKMapView alloc] initWithFrame:self.view.frame];
  mapView_.alpha = 0.0;
  mapView_.delegate = self;
  [self.view addSubview:mapView_];
  [mapView_ release];

  self.filterButtons =
      [NSArray arrayWithObjects:(id)foodFilterButton_,
                                (id)booksFilterButton_,
                                (id)filmFilterButton_,
                                (id)musicFilterButton_,
                                (id)otherFilterButton_, nil];
  
  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.filterView = nil;
  self.filterButtons = nil;
  self.foodFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmFilterButton = nil;
  self.musicFilterButton = nil;
  self.otherFilterButton = nil;
  self.selectedFilterButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self loadStampsFromDataStore];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:YES];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:NO];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)loadStampsFromDataStore {
  self.entitiesArray = nil;
	NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  [request setPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
	NSArray* results = [Stamp objectsWithFetchRequest:request];
  results = [results valueForKeyPath:@"@distinctUnionOfObjects.entityObject"];
  descriptor = [NSSortDescriptor sortDescriptorWithKey:@"stamps.@max.created" ascending:NO];
  self.entitiesArray =
      [NSMutableArray arrayWithArray:[results sortedArrayUsingDescriptors:[NSArray arrayWithObject:descriptor]]];
  [self filterStamps];
  self.tableView.contentOffset = scrollPosition_;
}

- (void)loadStampsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  NSString* path = kInboxPath;
  if (entitiesArray_.count == 0)
    path = kEverythingPath;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:@"1", @"quality", nil];
  [objectLoader send];
}

- (void)stampWasCreated:(NSNotification*)notification {
  [self loadStampsFromDataStore];
}

#pragma mark - Filter stuff

- (IBAction)filterButtonPushed:(id)sender {
  self.filteredEntitiesArray = nil;

  UIButton* selectedButton = (UIButton*)sender;
  for (UIButton* button in self.filterButtons)
    button.selected = (button == selectedButton && !button.selected);

  self.selectedFilterButton = selectedButton;
  if (selectedButton && !selectedButton.selected)
    self.selectedFilterButton = nil;
  
  [self filterStamps];
}

- (void)filterStamps {
  if (!self.selectedFilterButton) {
    // No need to filter.
    self.filteredEntitiesArray = entitiesArray_;
    [self.tableView reloadData];
    return;
  }
  
  NSString* filterString = nil;
  if (self.selectedFilterButton == foodFilterButton_) {
    filterString = @"food";
  } else if (self.selectedFilterButton == booksFilterButton_) {
    filterString = @"book";
  } else if (self.selectedFilterButton == filmFilterButton_) {
    filterString = @"film";
  } else if (self.selectedFilterButton == musicFilterButton_) {
    filterString = @"music";
  } else if (self.selectedFilterButton == otherFilterButton_) {
    filterString = @"other";
  }
  if (filterString) {
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"category == %@", filterString];
    self.filteredEntitiesArray =
        [NSMutableArray arrayWithArray:[entitiesArray_ filteredArrayUsingPredicate:filterPredicate]];
    [self.tableView reloadData];
  }
}

#pragma mark - Table view data source

- (void)tableView:(UITableView*)tableView willBeginEditingRowAtIndexPath:(NSIndexPath*)indexPath {
  //InboxTableViewCell* cell = (InboxTableViewCell*)[tableView cellForRowAtIndexPath:indexPath];
}

- (void)tableView:(UITableView*)tableView didEndEditingRowAtIndexPath:(NSIndexPath*)indexPath {
  //UITableViewCell* cell = [tableView cellForRowAtIndexPath:indexPath];
}

- (UITableViewCellEditingStyle)tableView:(UITableView*)tableView
           editingStyleForRowAtIndexPath:(NSIndexPath*)indexPath {
  return UITableViewCellEditingStyleDelete;
}

- (void)tableView:(UITableView*)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath*)indexPath {
  if (editingStyle == UITableViewCellEditingStyleDelete) {
    /*Entity* e = [filteredEntitiesArray_ objectAtIndex:indexPath.row];
    [filteredEntitiesArray_ removeObjectAtIndex:indexPath.row];
    [self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
                          withRowAnimation:UITableViewRowAnimationBottom];*/
  }    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return [filteredEntitiesArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];

  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  cell.entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];

  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"InboxLastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
  for (Stamp* stamp in objects) {
    stamp.temporary = [NSNumber numberWithBool:NO];
    [stamp.managedObjectContext save:NULL];
  }
	[self loadStampsFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadStampsFromNetwork];
    return;
  }

  [self setIsLoading:NO];
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor whiteColor];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Entity* entity = [filteredEntitiesArray_ objectAtIndex:indexPath.row];
  Stamp* stamp = nil;
  if (entity.stamps.count > 0) {
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
    NSArray* sortedStamps = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    sortedStamps = [sortedStamps filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
    stamp = [sortedStamps lastObject];
  } else {
    stamp = [entity.stamps anyObject];
  }
  
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - STReloadableTableView methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadStampsFromNetwork];
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadAllPanes
                                                      object:self];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadStampsFromNetwork];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [[NSNotificationCenter defaultCenter] postNotificationName:kInboxTableDidScrollNotification
                                                      object:scrollView];
  [super scrollViewDidScroll:scrollView];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  [super scrollViewDidEndDragging:scrollView willDecelerate:decelerate];
}

#pragma mark - Map stuff.

- (void)addAnnotationForEntity:(Entity*)entity {
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","]; 
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];
  annotation.stamp = [entity.stamps anyObject];
  
  [mapView_ addAnnotation:annotation];
  [annotation release];
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

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:profileViewController animated:YES];
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
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:annotation.stamp];
  
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - MKMapViewDelegate Methods

- (void)mapView:(MKMapView*)mapView didUpdateUserLocation:(MKUserLocation*)userLocation {
  if (!userPannedMap_) {
    CLLocationCoordinate2D currentLocation = mapView_.userLocation.location.coordinate;
    MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kStandardLatLongSpan, kStandardLatLongSpan);
    MKCoordinateRegion region = MKCoordinateRegionMake(currentLocation, mapSpan);
    [mapView setRegion:region animated:YES];
  }
}

- (void)mapView:(MKMapView*)mapView regionDidChangeAnimated:(BOOL)animated {
  userPannedMap_ = YES;
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
  UserImageView* userImageView = [[UserImageView alloc] initWithFrame:CGRectMake(0, 0, kMapUserImageSize, kMapUserImageSize)];
  userImageView.enabled = YES;
  [userImageView addTarget:self
                    action:@selector(mapUserTapped:)
          forControlEvents:UIControlEventTouchUpInside];
  userImageView.imageURL = [(STPlaceAnnotation*)annotation stamp].user.profileImageURL;
  pinView.leftCalloutAccessoryView = userImageView;
  [userImageView release];
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.canShowCallout = YES;
  pinView.animatesDrop = YES;
  return pinView;
}


@end
