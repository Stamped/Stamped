//
//  InboxViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxViewController.h"

#import <CoreText/CoreText.h>
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
#import "STStampFilterBar.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kMapUserImageSize = 32.0;
static NSString* const kInboxPath = @"/collections/inbox.json";

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)filterStamps;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)userLoggedOut:(NSNotification*)notification;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)mapUserTapped:(id)sender;
- (void)mapDisclosureTapped:(id)sender;
- (void)appDidBecomeActive:(NSNotification*)notification;

- (void)managedObjectContextChanged:(NSNotification*)notification;

@property (nonatomic, assign) BOOL userPannedMap;
@property (nonatomic, assign) BOOL needToRefetch;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@property (nonatomic, retain) NSIndexPath* selectedIndexPath;

@end

@implementation InboxViewController

@synthesize mapView = mapView_;
@synthesize needToRefetch = needToRefetch_;
@synthesize userPannedMap = userPannedMap_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize selectedIndexPath = selectedIndexPath_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.searchQuery = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.selectedIndexPath = nil;
  [super dealloc];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  if (!self.view.superview)
    return;

  userPannedMap_ = NO;
  [self.stampFilterBar.searchField resignFirstResponder];
  self.tableView.scrollEnabled = NO;
  self.fetchedResultsController.fetchRequest.predicate =
      [NSPredicate predicateWithFormat:@"(SUBQUERY(stamps, $s, $s.temporary == NO AND $s.deleted == NO).@count != 0)"];
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
  NSArray* entitiesArray = [sectionInfo objects];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Entity* e in entitiesArray) {
                       if (!e.coordinates)
                         continue;
                      [self addAnnotationForEntity:e];
                     }
                   }];
}

- (void)listButtonWasPressed:(NSNotification*)notification {
  if (!self.view.superview)
    return;

  self.tableView.scrollEnabled = YES;
  [self filterStamps];
  [mapView_ removeAnnotations:mapView_.annotations];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 0.0; }
                   completion:^(BOOL finished) { mapView_.showsUserLocation = NO; }];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:self.view.bounds];
  scrollView.scrollsToTop = NO;
  UIImageView* emptyView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"empty_inbox"]];
  [scrollView addSubview:emptyView];
  [emptyView release];
  [self.view insertSubview:scrollView atIndex:0];
  scrollView.delegate = self;
  scrollView.alwaysBounceVertical = YES;
  scrollView.contentSize = self.view.frame.size;
  [scrollView release];
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(userLoggedOut:)
                                               name:kUserHasLoggedOutNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(managedObjectContextChanged:)
                                               name:NSManagedObjectContextObjectsDidChangeNotification
                                             object:[Entity managedObjectContext]];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(appDidBecomeActive:)
                                               name:UIApplicationDidBecomeActiveNotification
                                             object:nil];
  mapView_ = [[MKMapView alloc] initWithFrame:self.view.frame];
  mapView_.alpha = 0.0;
  mapView_.delegate = self;
  [self.view addSubview:mapView_];
  [mapView_ release];

  self.stampFilterBar.filterType = selectedFilterType_;
  self.stampFilterBar.searchQuery = searchQuery_;

  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  if (needToRefetch_) {
    NSError* error;
    if (![self.fetchedResultsController performFetch:&error]) {
      // Update to handle the error appropriately.
      NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
    }
    needToRefetch_ = NO;
    [self.tableView reloadData];
    [self.tableView selectRowAtIndexPath:self.selectedIndexPath
                                animated:NO
                          scrollPosition:UITableViewScrollPositionNone];
  }
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (mapView_.alpha > 0)
    mapView_.showsUserLocation = YES;

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:YES];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"InboxLastUpdatedAt"]];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  self.selectedIndexPath = [self.tableView indexPathForSelectedRow];
  mapView_.showsUserLocation = NO;
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:NO];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)managedObjectContextChanged:(NSNotification*)notification {
  NSSet* objects = [NSSet setWithSet:[notification.userInfo objectForKey:NSUpdatedObjectsKey]];
  objects = [objects setByAddingObjectsFromSet:[notification.userInfo objectForKey:NSInsertedObjectsKey]];
  
  NSSet* stamps = [objects objectsPassingTest:^BOOL(id obj, BOOL* stop) {
    return ([obj isMemberOfClass:[Stamp class]] && ![[(Stamp*)obj temporary] boolValue] && ![[(Stamp*)obj deleted] boolValue]);
  }];

  for (Stamp* s in stamps) {
    Entity* e = s.entityObject;
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    NSArray* filteredStamps = [[e.stamps allObjects] filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO && deleted == NO"]];
    filteredStamps = [filteredStamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    Stamp* latestStamp = [filteredStamps objectAtIndex:0];
    e.mostRecentStampDate = latestStamp.created;
  }
  
  User* currentUser = [AccountManager sharedManager].currentUser;
  BOOL shouldHideShelfAndTable = NO;
  if (currentUser && currentUser.numStamps.integerValue == 0 && currentUser.following.count == 0)
    shouldHideShelfAndTable = YES;
  
  self.tableView.hidden = shouldHideShelfAndTable;

  NSString* currentUserID = currentUser.userID;
  NSSet* allStampsOrCurrentUser = [objects objectsPassingTest:^BOOL(id obj, BOOL* stop) {
    if ([obj isMemberOfClass:[Stamp class]] ||
        ([obj isMemberOfClass:[User class]] && [[(User*)obj userID] isEqualToString:currentUserID])) {
      *stop = YES;
      return YES;
    }
    return NO;
  }];

  if (allStampsOrCurrentUser.count > 0)
    needToRefetch_ = YES;
}

- (void)loadStampsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Entity fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"mostRecentStampDate" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:
        [NSPredicate predicateWithFormat:@"(SUBQUERY(stamps, $s, $s.temporary == NO AND $s.deleted == NO).@count != 0)"]];
    [request setFetchBatchSize:20];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Entity managedObjectContext]
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

- (void)loadStampsFromNetwork {
  [self setIsLoading:YES];
  // In case of inbox having zero stamps...
  NSTimeInterval latestTimestamp = 0;
  NSDate* lastUpdated = [[NSUserDefaults standardUserDefaults] objectForKey:@"InboxLatestStampModified"];
  if (lastUpdated)
    latestTimestamp = lastUpdated.timeIntervalSince1970;
  
  NSString* latestTimestampString = [NSString stringWithFormat:@"%.0f", latestTimestamp];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kInboxPath delegate:self];
  objectLoader.objectMapping = stampMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:@"1", @"quality",
                         latestTimestampString, @"since",
                         @"modified", @"sort",
                         nil];
  NSDate* oldestTimeInBatch = [[NSUserDefaults standardUserDefaults] objectForKey:@"InboxOldestTimestampInBatch"];
  if (oldestTimeInBatch && oldestTimeInBatch.timeIntervalSince1970 > 0) {
    NSString* oldestTimeInBatchString = [NSString stringWithFormat:@"%.0f", oldestTimeInBatch.timeIntervalSince1970];
    [params setObject:oldestTimeInBatchString forKey:@"before"];
  }
  objectLoader.params = params;
  [objectLoader send];
}

- (void)stampWasCreated:(NSNotification*)notification {      
  [self.tableView setContentOffset:CGPointZero];
}

- (void)userLoggedOut:(NSNotification*)notification {
  // Do something if the user logs out?
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

#pragma mark - Filter/Search stuff.

- (void)filterStamps {
  NSMutableArray* predicates = [NSMutableArray array];
  [predicates addObject:[NSPredicate predicateWithFormat:@"(SUBQUERY(stamps, $s, $s.temporary == NO AND $s.deleted == NO).@count != 0)"]];

  if (searchQuery_.length) {
    NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;

      NSPredicate* p = [NSPredicate predicateWithFormat:
          @"((ANY stamps.blurb contains[cd] %@) OR (ANY stamps.user.screenName contains[cd] %@) OR (title contains[cd] %@) OR (subtitle contains[cd] %@))",
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
      break;
  }
  if (filterString)
    [predicates addObject:[NSPredicate predicateWithFormat:@"category == %@", filterString]];

  self.fetchedResultsController.fetchRequest.predicate = [NSCompoundPredicate andPredicateWithSubpredicates:predicates];
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  return [sectionInfo numberOfObjects];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];

  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  [self configureCell:cell atIndexPath:indexPath];

  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSMutableArray* toDelete = [NSMutableArray array];
  for (Stamp* stamp in objects) {
    if ([stamp.deleted boolValue]) {
      [toDelete addObject:stamp];
    } else {
      stamp.temporary = [NSNumber numberWithBool:NO];
    }
  }
  
  Stamp* oldestStampInBatch = objects.lastObject;
  if (oldestStampInBatch.modified) {
    [[NSUserDefaults standardUserDefaults] setObject:oldestStampInBatch.modified
                                              forKey:@"InboxOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  for (Stamp* stamp in toDelete) {
    if (stamp.entityObject.stamps.count > 1) {
      NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
      NSMutableArray* sortedStamps =
          [NSMutableArray arrayWithArray:[[stamp.entityObject.stamps allObjects] sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]]];
      [sortedStamps removeObject:stamp];
      Stamp* latestStamp = [sortedStamps objectAtIndex:0];
      stamp.entityObject.mostRecentStampDate = latestStamp.created;
    }

    [Stamp.managedObjectContext deleteObject:stamp];
  }
  [Stamp.managedObjectContext save:NULL];

  if (objects.count < 10) {
    // Grab latest stamp.
    NSFetchRequest* request = [Stamp fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"modified" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
    [request setFetchLimit:1];
    Stamp* latestStamp = [Stamp objectWithFetchRequest:request];

    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"InboxOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] setObject:latestStamp.modified
                                              forKey:@"InboxLatestStampModified"];
    NSDate* now = [NSDate date];
    [[NSUserDefaults standardUserDefaults] setObject:now forKey:@"InboxLastUpdatedAt"];
    [[NSUserDefaults standardUserDefaults] synchronize];
    [self updateLastUpdatedTo:now];
    [self setIsLoading:NO];
  } else {
    [self loadStampsFromNetwork];
  }
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

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  [(InboxTableViewCell*)cell setEntityObject:(Entity*)[fetchedResultsController_ objectAtIndexPath:indexPath]];
}

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  self.selectedIndexPath = [self.tableView indexPathForSelectedRow];
  [self.tableView reloadData];
  [self.tableView selectRowAtIndexPath:self.selectedIndexPath
                              animated:NO
                        scrollPosition:UITableViewScrollPositionNone];
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor whiteColor];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Entity* entity = [fetchedResultsController_ objectAtIndexPath:indexPath];

  Stamp* stamp = nil;
  if (entity.stamps.count > 0) {
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
    NSArray* sortedStamps = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    sortedStamps = [sortedStamps filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO AND deleted == NO"]];
    stamp = [sortedStamps lastObject];
  } else {
    stamp = [entity.stamps anyObject];
  }
  
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - STTableViewController methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"InboxOldestTimestampInBatch"];
  [[NSUserDefaults standardUserDefaults] synchronize];
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
  if (self.stampFilterBar.searchQuery.length)
    [self.stampFilterBar.searchField resignFirstResponder];

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

  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
  NSArray* stampsArray = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO AND deleted == NO"]];

  annotation.stamp = [stampsArray lastObject];
  
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

- (void)appDidBecomeActive:(NSNotification*)notification {
  [self.tableView reloadData];
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
  return pinView;
}


@end
