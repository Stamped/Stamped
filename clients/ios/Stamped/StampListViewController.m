//
//  StampListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampListViewController.h"

#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "AccountManager.h"
#import "STNavigationBar.h"
#import "STPlaceAnnotation.h"
#import "ProfileViewController.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"
#import "STStampFilterBar.h"
#import "STMapToggleButton.h"
#import "STMapViewController.h"

static const CGFloat kMapUserImageSize = 32.0;
static NSString* const kUserStampsPath = @"/collections/user.json";

@interface StampListViewController ()
- (void)showMapView;
- (void)showListView;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)addAnnotationForStamp:(Stamp*)stamp;
- (void)mapUserTapped:(id)sender;
- (void)mapDisclosureTapped:(id)sender;
- (void)loadStampsFromNetwork;
- (void)loadStampsFromDataStore;
- (void)filterStamps;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;

@property (nonatomic, retain) STMapViewController* mapViewController;
@property (nonatomic, assign) BOOL mapViewShown;
@property (nonatomic, readonly) MKMapView* mapView;
@property (nonatomic, assign) BOOL userPannedMap;
@property (nonatomic, retain) NSDate* oldestInBatch;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@end

@implementation StampListViewController

@synthesize mapViewController = mapViewController_;
@synthesize mapViewShown = mapViewShown_;
@synthesize stampsAreTemporary = stampsAreTemporary_;
@synthesize user = user_;
@synthesize oldestInBatch = oldestInBatch_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize userPannedMap = userPannedMap_;
@synthesize mapView = mapView_;
@synthesize fetchedResultsController = fetchedResultsController_;

- (id)init {
  self = [self initWithNibName:@"StampListViewController" bundle:nil];
  if (self) {
    self.disableReload = YES;
    self.mapViewController = [[[STMapViewController alloc] init] autorelease];
  }
  return self;
}

- (void)dealloc {
  self.user = nil;
  self.oldestInBatch = nil;
  self.searchQuery = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.mapViewController = nil;
  mapView_ = nil;
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (mapViewShown_) {
    [self.view.superview insertSubview:self.mapViewController.view atIndex:0];
    self.view.hidden = YES;
    [self.mapViewController viewWillAppear:animated];
  } else {
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow
                                  animated:animated];
  }
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (mapViewShown_)
    [self.mapViewController viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  if (mapViewShown_)
    [self.mapViewController viewWillDisappear:animated];

  mapView_.showsUserLocation = NO;
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  if (mapViewShown_)
    [self.mapViewController viewDidDisappear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];

  STMapToggleButton* toggleButton = [[[STMapToggleButton alloc] init] autorelease];
  [toggleButton.mapButton addTarget:self action:@selector(showMapView) forControlEvents:UIControlEventTouchUpInside];
  [toggleButton.listButton addTarget:self action:@selector(showListView) forControlEvents:UIControlEventTouchUpInside];
  UIBarButtonItem* rightItem = [[[UIBarButtonItem alloc] initWithCustomView:toggleButton] autorelease];
  self.navigationItem.rightBarButtonItem = rightItem;

  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.tableView = nil;
  self.stampFilterBar = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)setStampsAreTemporary:(BOOL)stampsAreTemporary {
  stampsAreTemporary_ = stampsAreTemporary;
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];

  for (Stamp* stamp in [sectionInfo objects]) {
    stamp.temporary = [NSNumber numberWithBool:stampsAreTemporary];
  }

  [Stamp.managedObjectContext save:NULL];
}

- (void)filterStamps {
  NSMutableArray* predicates = [NSMutableArray array];
  [predicates addObject:[NSPredicate predicateWithFormat:@"deleted == NO AND user.userID == %@", user_.userID]];
  
  if (searchQuery_.length) {
    NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;
      
      NSPredicate* p = [NSPredicate predicateWithFormat:
                        @"((blurb contains[cd] %@) OR (user.screenName contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
                        term, term, term, term];
      [predicates addObject:p];
    }
  }
  
  NSString* filterString = nil;
  switch (selectedFilterType_) {
    case StampFilterTypeBook:
      filterString = @"book";
      break;
    case StampFilterTypeFood:
      filterString = @"food";
      break;
    case StampFilterTypeFilm:
      filterString = @"film";
      break;
    case StampFilterTypeMusic:
      filterString = @"music";
      break;
    case StampFilterTypeOther:
      filterString = @"other";
      break;
    default:
      NSLog(@"Invalid filter string...");
      break;
  }

  if (filterString)
    [predicates addObject:[NSPredicate predicateWithFormat:@"entityObject.category == %@", filterString]];
  
  self.fetchedResultsController.fetchRequest.predicate = [NSCompoundPredicate andPredicateWithSubpredicates:predicates];
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
}

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  [(InboxTableViewCell*)cell setStamp:(Stamp*)[fetchedResultsController_ objectAtIndexPath:indexPath]];
}

- (void)showMapView {
  [mapViewController_ viewWillAppear:YES];
  [self viewWillDisappear:YES];

  mapViewController_.source = STMapViewControllerSourceInbox;
  mapViewController_.view.hidden = NO;
  [UIView transitionFromView:self.view
                      toView:mapViewController_.view
                    duration:1
                     options:UIViewAnimationOptionTransitionFlipFromRight
                  completion:^(BOOL finished) {
                    [self viewDidDisappear:YES];
                    [mapViewController_ viewDidAppear:YES];
                    mapViewShown_ = YES;
                  }];
}

- (void)showListView {
  [mapViewController_.view.superview insertSubview:self.view atIndex:0];
  [self viewWillAppear:YES];
  [mapViewController_ viewWillDisappear:YES];
  [UIView transitionFromView:mapViewController_.view
                      toView:self.view
                    duration:1
                     options:(UIViewAnimationOptionTransitionFlipFromLeft | UIViewAnimationOptionShowHideTransitionViews)
                  completion:^(BOOL finished) {
                    [mapViewController_ viewDidDisappear:YES];
                    [self viewDidAppear:YES];
                    mapViewShown_ = NO;
                  }];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  userPannedMap_ = NO;
  self.tableView.scrollEnabled = NO;
  [self.stampFilterBar.searchField resignFirstResponder];
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
  NSArray* stampsArray = [sectionInfo objects];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Stamp* s in stampsArray) {
                       if (!s.entityObject.coordinates)
                         continue;
                       [self addAnnotationForStamp:s];
                     }
                   }];
}

- (void)listButtonWasPressed:(NSNotification*)notification {
  self.tableView.scrollEnabled = YES;
  [mapView_ removeAnnotations:mapView_.annotations];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 0.0; }
                   completion:^(BOOL finished) { mapView_.showsUserLocation = NO; }];
}

#pragma mark - Map stuff.

- (void)addAnnotationForStamp:(Stamp*)stamp {
  Entity* e = stamp.entityObject;
  NSArray* coordinates = [e.coordinates componentsSeparatedByString:@","];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];
  annotation.stamp = stamp;
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
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:annotation.stamp];
  
  // Pass the selected object to the new view controller.
  [self.navigationController pushViewController:detailViewController animated:YES];
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
  userImageView.imageURL = [[(STPlaceAnnotation*)annotation stamp].user profileImageURLForSize:ProfileImageSize37];
  pinView.leftCalloutAccessoryView = userImageView;
  [userImageView release];
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.canShowCallout = YES;
  return pinView;
}

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query {
  self.searchQuery = query;
  selectedFilterType_ = filterType;
  [self filterStamps];

  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  return [sectionInfo numberOfObjects];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (!cell)
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

  [self configureCell:cell atIndexPath:indexPath];
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [fetchedResultsController_ objectAtIndexPath:indexPath];
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath rangeOfString:kUserStampsPath].location != NSNotFound) {
    self.oldestInBatch = [objects.lastObject created];

    self.stampsAreTemporary = stampsAreTemporary_;  // Just fire off the setters logic.
    if (objects.count < 10 || !self.oldestInBatch) {
      self.oldestInBatch = nil;
    } else {
      [self loadStampsFromNetwork];
    }
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [objectLoader send];
    return;
  }
}

- (void)loadStampsFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserStampsPath
                                                                    delegate:self];
  objectLoader.objectMapping = stampMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id",
      @"1", @"quality", @"0", @"since", nil];
  if (oldestInBatch_)
    [params setObject:[NSString stringWithFormat:@"%.0f", oldestInBatch_.timeIntervalSince1970] forKey:@"before"];

  objectLoader.params = params;
  [objectLoader send];
}

- (void)loadStampsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Stamp fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:[NSPredicate predicateWithFormat:@"deleted == NO AND user.userID == %@", user_.userID]];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Stamp managedObjectContext]
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
  }
}

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerWillChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView beginUpdates];
}

- (void)controller:(NSFetchedResultsController*)controller 
   didChangeObject:(id)anObject
       atIndexPath:(NSIndexPath*)indexPath
     forChangeType:(NSFetchedResultsChangeType)type
      newIndexPath:(NSIndexPath*)newIndexPath {
  
  UITableView* tableView = self.tableView;
  
  switch(type) {
    case NSFetchedResultsChangeInsert:
      [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath] withRowAnimation:UITableViewRowAnimationNone];
      break;
      
    case NSFetchedResultsChangeDelete:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
      break;
      
    case NSFetchedResultsChangeUpdate:
      [self configureCell:[tableView cellForRowAtIndexPath:indexPath] atIndexPath:indexPath];
      break;
      
    case NSFetchedResultsChangeMove:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
      [tableView reloadSections:[NSIndexSet indexSetWithIndex:newIndexPath.section] withRowAnimation:UITableViewRowAnimationNone];
      break;
  }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView endUpdates];
}

@end
