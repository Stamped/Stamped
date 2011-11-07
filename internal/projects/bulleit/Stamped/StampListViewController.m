//
//  StampListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampListViewController.h"

#import <RestKit/CoreData/CoreData.h>

#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "AccountManager.h"
#import "STNavigationBar.h"
#import "STPlaceAnnotation.h"
#import "ProfileViewController.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kMapUserImageSize = 32.0;
static NSString* const kUserStampsPath = @"/collections/user.json";

@interface StampListViewController ()
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)addAnnotationForStamp:(Stamp*)stamp;
- (void)mapUserTapped:(id)sender;
- (void)mapDisclosureTapped:(id)sender;
- (void)loadStampsFromNetwork;
- (void)loadStampsFromDataStore;
- (void)filterStamps;

@property (nonatomic, readonly) MKMapView* mapView;
@property (nonatomic, assign) BOOL userPannedMap;
@property (nonatomic, retain) NSDate* oldestInBatch;
@property (nonatomic, copy) NSArray* stampsArray;
@property (nonatomic, copy) NSArray* filteredStampsArray;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@end

@implementation StampListViewController

@synthesize tableView = tableView_;
@synthesize stampsArray = stampsArray_;
@synthesize filteredStampsArray = filteredStampsArray_;
@synthesize stampsAreTemporary = stampsAreTemporary_;
@synthesize user = user_;
@synthesize oldestInBatch = oldestInBatch_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize stampFilterBar = stampFilterBar_;
@synthesize userPannedMap = userPannedMap_;
@synthesize mapView = mapView_;

- (id)init {
  self = [self initWithNibName:@"StampListViewController" bundle:nil];
  if (self) {
    stampsAreTemporary_ = YES;
  }
  return self;
}

- (void)dealloc {
  self.user = nil;
  self.stampsArray = nil;
  self.tableView = nil;
  self.oldestInBatch = nil;
  self.searchQuery = nil;
  self.stampFilterBar = nil;
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  [navBar setButtonShown:YES];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  [navBar setButtonShown:NO];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  mapView_ = [[MKMapView alloc] initWithFrame:self.view.frame];
  mapView_.alpha = 0.0;
  mapView_.delegate = self;
  [self.view addSubview:mapView_];
  [mapView_ release];

  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(mapButtonWasPressed:)
                                               name:kMapViewButtonPressedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(listButtonWasPressed:)
                                               name:kListViewButtonPressedNotification
                                             object:nil];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.tableView = nil;
  self.stampFilterBar = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)setStampsAreTemporary:(BOOL)stampsAreTemporary {
  stampsAreTemporary_ = stampsAreTemporary;
  
  for (Stamp* stamp in stampsArray_) {
    stamp.temporary = [NSNumber numberWithBool:stampsAreTemporary];
    [stamp.managedObjectContext save:NULL];
  }
}

- (void)filterStamps {
  if (selectedFilterType_ == StampFilterTypeNone) {
    // No need to filter.
    self.filteredStampsArray = [NSArray arrayWithArray:stampsArray_];
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
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"entityObject.category == %@", filterString];
    self.filteredStampsArray = [stampsArray_ filteredArrayUsingPredicate:filterPredicate];
  }
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  userPannedMap_ = NO;
  self.tableView.scrollEnabled = NO;
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Stamp* s in stampsArray_) {
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
  userImageView.imageURL = [(STPlaceAnnotation*)annotation stamp].user.profileImageURL;
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
  if (![query isEqualToString:searchQuery_]) {
    self.searchQuery = query;
    [self loadStampsFromDataStore];
  }

  selectedFilterType_ = filterType;
  [self filterStamps];
  
  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return self.filteredStampsArray.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (!cell)
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

  cell.stamp = (Stamp*)[filteredStampsArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [filteredStampsArray_ objectAtIndex:indexPath.row];
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath rangeOfString:kUserStampsPath].location != NSNotFound) {
    NSMutableArray* toDelete = [NSMutableArray array];
    NSMutableArray* mutableObjects = [NSMutableArray array];
    for (Stamp* stamp in objects) {
      if ([stamp.deleted boolValue]) {
        [toDelete addObject:stamp];
      } else {
        [mutableObjects addObject:stamp];
      }
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
    
    self.oldestInBatch = [mutableObjects.lastObject modified];

    [self loadStampsFromDataStore];
    self.stampsAreTemporary = stampsAreTemporary_;  // Just fire off the setters logic.
    if (mutableObjects.count < 10 || !self.oldestInBatch) {
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
  self.stampsArray = nil;
  NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];

  NSPredicate* p = [NSPredicate predicateWithFormat:@"user.screenName == %@", user_.screenName];
  if (searchTerms.count == 1 && searchQuery_.length) {
    p = [NSPredicate predicateWithFormat:
         @"(user.screenName == %@) AND ((blurb contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
         user_.screenName, searchQuery_, searchQuery_, searchQuery_, searchQuery_];
  } else if (searchTerms.count > 1) {
    NSMutableArray* subPredicates = [NSMutableArray array];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;
      
      NSPredicate* p = [NSPredicate predicateWithFormat:
                        @"(user.screenName == %@) AND ((blurb contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
                        user_.screenName, term, term, term, term];
      [subPredicates addObject:p];
    }
    p = [NSCompoundPredicate andPredicateWithSubpredicates:subPredicates];
  }
  NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  [request setPredicate:p];
	self.stampsArray = [Stamp objectsWithFetchRequest:request];
  
  [self filterStamps];
  [self.tableView reloadData];
}


@end
