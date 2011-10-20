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
#import "STStampFilterBar.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kMapUserImageSize = 32.0;
static NSString* const kInboxPath = @"/collections/inbox.json";

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)sortStamps;
- (void)filterStamps;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)userLoggedOut:(NSNotification*)notification;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)mapUserTapped:(id)sender;
- (void)mapDisclosureTapped:(id)sender;

- (void)managedObjectContextChanged:(NSNotification*)notification;

@property (nonatomic, retain) NSMutableArray* entitiesArray;
@property (nonatomic, retain) NSMutableArray* filteredEntitiesArray;
@property (nonatomic, assign) BOOL userPannedMap;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, assign) StampSortType selectedSortType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;

@end

@implementation InboxViewController

@synthesize mapView = mapView_;
@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize userPannedMap = userPannedMap_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize selectedSortType = selectedSortType_;
@synthesize searchQuery = searchQuery_;
@synthesize stampFilterBar = stampFilterBar_;
@synthesize fetchedResultsController = fetchedResultsController_;

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.searchQuery = nil;
  self.stampFilterBar = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  [super dealloc];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  CGRect mapFrame = mapView_.frame;
  mapFrame.origin.y = self.tableView.contentOffset.y;
  mapView_.frame = mapFrame;
  [self.tableView scrollRectToVisible:mapFrame animated:NO];
  userPannedMap_ = NO;
  self.tableView.scrollEnabled = NO;
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Entity* e in self.entitiesArray) {
                       if (!e.coordinates)
                         continue;
                      [self addAnnotationForEntity:e];
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(userLoggedOut:)
                                               name:kUserHasLoggedOutNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(managedObjectContextChanged:)
                                               name:NSManagedObjectContextObjectsDidChangeNotification
                                             object:[Entity managedObjectContext]];
  mapView_ = [[MKMapView alloc] initWithFrame:self.view.frame];
  mapView_.alpha = 0.0;
  mapView_.delegate = self;
  [self.view addSubview:mapView_];
  [mapView_ release];

  stampFilterBar_.filterType = selectedFilterType_;
  stampFilterBar_.sortType = selectedSortType_;
  stampFilterBar_.searchQuery = searchQuery_;

  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.stampFilterBar = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (mapView_.alpha > 0)
    mapView_.showsUserLocation = YES;
  
  if (stampFilterBar_.sortType == StampSortTypeDistance)
    [stampFilterBar_.locationManager startUpdatingLocation];

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:YES];
  [self loadStampsFromDataStore];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];

  mapView_.showsUserLocation = NO;
  [stampFilterBar_.locationManager stopUpdatingLocation];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:NO];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)managedObjectContextChanged:(NSNotification*)notification {
  NSSet* objects = [NSSet setWithSet:[notification.userInfo objectForKey:NSUpdatedObjectsKey]];
  objects = [objects setByAddingObjectsFromSet:[notification.userInfo objectForKey:NSInsertedObjectsKey]];
  objects = [objects objectsPassingTest:^BOOL(id obj, BOOL* stop) {
    if ([obj isMemberOfClass:[Stamp class]] && ![[(Stamp*)obj temporary] boolValue])
      return YES;

    return NO;
  }];

  if (objects.count > 0) {
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    NSArray* sortedStamps = [[objects allObjects] sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    Stamp* latestStamp = [sortedStamps objectAtIndex:0];
    Entity* entity = latestStamp.entityObject;
    if (!entity.mostRecentStampDate ||
        [latestStamp.created timeIntervalSinceDate:entity.mostRecentStampDate] > 0) {
      latestStamp.entityObject.mostRecentStampDate = latestStamp.created;
    }
  }
  
  // TODO(andybons): Deal with when we remove stamps.
  //NSLog(@"Deleted objects %@", [notification.userInfo objectForKey:NSDeletedObjectsKey]);
}

- (void)loadStampsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Entity fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"mostRecentStampDate" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Entity managedObjectContext]
                                              sectionNameKeyPath:nil
                                                       cacheName:@"InboxItems"];
    self.fetchedResultsController = fetchedResultsController;
    fetchedResultsController.delegate = self;
    [fetchedResultsController release];
  }

  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
  
  self.entitiesArray = nil;
  NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];
  
  NSPredicate* p = [NSPredicate predicateWithFormat:@"temporary == NO"];
  if (searchTerms.count == 1 && searchQuery_.length) {
    p = [NSPredicate predicateWithFormat:
         @"(temporary == NO) AND ((blurb contains[cd] %@) OR (user.screenName contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
         searchQuery_, searchQuery_, searchQuery_, searchQuery_];
  } else if (searchTerms.count > 1) {
    NSMutableArray* subPredicates = [NSMutableArray array];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;

      NSPredicate* p = [NSPredicate predicateWithFormat:
          @"(temporary == NO) AND ((blurb contains[cd] %@) OR (user.screenName contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
          term, term, term, term];
      [subPredicates addObject:p];
    }
    p = [NSCompoundPredicate andPredicateWithSubpredicates:subPredicates];
  }
  NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  [request setPredicate:p];
	NSArray* results = [Stamp objectsWithFetchRequest:request];
  NSMutableArray* sortedEntities = [NSMutableArray arrayWithCapacity:results.count];
  for (Stamp* s in results) {
    if (s.entityObject && ![sortedEntities containsObject:s.entityObject])
      [sortedEntities addObject:s.entityObject];
  }
  self.entitiesArray = sortedEntities;

  [self filterStamps];
  [self sortStamps];
  [self.tableView reloadData];
  self.tableView.contentOffset = scrollPosition_;
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
  [self loadStampsFromDataStore];
}

- (void)userLoggedOut:(NSNotification*)notification {
  [self loadStampsFromDataStore];
}

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
          withSortType:(StampSortType)sortType
              andQuery:(NSString*)query {
  if (query && ![query isEqualToString:searchQuery_]) {
    self.searchQuery = query;
    selectedFilterType_ = filterType;
    selectedSortType_ = sortType;
    [self loadStampsFromDataStore];
    return;
  }

  selectedFilterType_ = filterType;
  [self filterStamps];

  selectedSortType_ = sortType;
  [self sortStamps];

  [self.tableView reloadData];
}

#pragma mark - Filter/Sort/Search stuff.

- (void)sortStamps {
  NSSortDescriptor* desc = nil;
  switch (selectedSortType_) {
    case StampSortTypeTime:
      desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
      break;
    case StampSortTypePopularity:
      desc = [NSSortDescriptor sortDescriptorWithKey:@"stamps.@count" ascending:NO];
      break;
    case StampSortTypeDistance: {
      CLLocation* currentLocation = stampFilterBar_.currentLocation;
      if (!currentLocation)
        break;

      NSArray* sortedEntities = [filteredEntitiesArray_ sortedArrayUsingComparator:^NSComparisonResult(id obj1, id obj2) {
        Entity* firstEntity = (Entity*)obj1;
        Entity* secondEntity = (Entity*)obj2;
        
        NSNumber* firstDistance = nil;
        NSNumber* secondDistance = nil;

        if (!firstEntity.location && !secondEntity.location)
          return NSOrderedSame;
        else if (!firstEntity.location && secondEntity.location)
          return NSOrderedDescending;
        else if (firstEntity.location && !secondEntity.location)
          return NSOrderedAscending;

        firstDistance = [NSNumber numberWithDouble:[firstEntity.location distanceFromLocation:currentLocation]];
        firstEntity.cachedDistance = firstDistance;
        secondDistance = [NSNumber numberWithDouble:[secondEntity.location distanceFromLocation:currentLocation]];
        secondEntity.cachedDistance = secondDistance;
        return [firstDistance compare:secondDistance];
      }];

      self.filteredEntitiesArray = [NSMutableArray arrayWithArray:sortedEntities];
      break;
    }
    default:
      break;
  }
  if (!desc)
    return;

  NSArray* sortedEntities = [filteredEntitiesArray_ sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  self.filteredEntitiesArray = [NSMutableArray arrayWithArray:sortedEntities];
}

- (void)filterStamps {
  if (selectedFilterType_ == StampFilterTypeNone) {
    // No need to filter.
    self.filteredEntitiesArray = [NSMutableArray arrayWithArray:entitiesArray_];
    return;
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
  if (filterString) {
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"category == %@", filterString];
    self.filteredEntitiesArray =
        [NSMutableArray arrayWithArray:[entitiesArray_ filteredArrayUsingPredicate:filterPredicate]];
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
  cell.sortType = selectedSortType_;
  cell.entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];

  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  selectedFilterType_ = StampFilterTypeNone;
  self.searchQuery = nil;
  selectedSortType_ = StampSortTypeTime;
  [stampFilterBar_ reset];

  for (Stamp* stamp in objects) {
    stamp.temporary = [NSNumber numberWithBool:NO];
    [stamp.managedObjectContext save:NULL];
  }

  Stamp* oldestStampInBatch = objects.lastObject;
  NSLog(@"Oldest timestamp in batch: %@", oldestStampInBatch.modified);
  [[NSUserDefaults standardUserDefaults] setObject:oldestStampInBatch.modified
                                            forKey:@"InboxOldestTimestampInBatch"];
  [[NSUserDefaults standardUserDefaults] synchronize];
  [self loadStampsFromDataStore];
  if (objects.count < 10) {
    // Grab latest stamp.
    NSFetchRequest* request = [Stamp fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"modified" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
    [request setFetchLimit:1];
    Stamp* latestStamp = [Stamp objectWithFetchRequest:request];

    NSLog(@"Storing latest stamp at time: %@", latestStamp.modified);
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"InboxOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] setObject:latestStamp.modified
                                              forKey:@"InboxLatestStampModified"];
    [[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"InboxLastUpdatedAt"];
    [[NSUserDefaults standardUserDefaults] synchronize];
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
  if (stampFilterBar_.searchQuery.length)
    [stampFilterBar_.searchField resignFirstResponder];

  [super scrollViewDidScroll:scrollView];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  [super scrollViewDidEndDragging:scrollView willDecelerate:decelerate];
}

#pragma mark - Map stuff.

- (void)addAnnotationForEntity:(Entity*)entity {
  // TODO(andybons): Replace with entity location method.
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];

  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
  NSArray* stampsArray = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];

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
