//
//  TodoViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/19/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "TodoViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Favorite.h"
#import "Notifications.h"
#import "STNavigationBar.h"
#import "STPlaceAnnotation.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "TodoTableViewCell.h"
#import "User.h"
#import "Util.h"
#import "Stamp.h"
#import "Alerts.h"

static NSString* const kShowFavoritesPath = @"/favorites/show.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";

@interface TodoViewController ()
- (void)loadFavoritesFromDataStore;
- (void)loadFavoritesFromNetwork;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)removeFavoriteWithEntityID:(NSString*)entityID;
- (void)addAnnotationForEntity:(Entity*)entity;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;
- (void)mapDisclosureTapped:(id)sender;
- (void)filterFavorites;

@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@property (nonatomic, readonly) MKMapView* mapView;
@property (nonatomic, assign) BOOL userPannedMap;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@end

@implementation TodoViewController

@synthesize delegate = delegate_;
@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize mapView = mapView_;
@synthesize userPannedMap = userPannedMap_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.delegate = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.searchQuery = nil;
  mapView_ = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)userPulledToReload {
  [self loadFavoritesFromNetwork];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadFavoritesFromNetwork];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  
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
  
  [self loadFavoritesFromDataStore];
  [self loadFavoritesFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.searchQuery = nil;
  mapView_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  NSArray* toDelete = [Favorite objectsWithPredicate:[NSPredicate predicateWithFormat:@"entityObject == NIL"]];
  for (Favorite* fave in toDelete)
    [Favorite.managedObjectContext deleteObject:fave];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  mapView_.showsUserLocation = NO;
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:NO];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];

  if (mapView_.alpha > 0)
    mapView_.showsUserLocation = YES;

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonShown:YES];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"TodoLastUpdatedAt"]];
}

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  Favorite* fave = [fetchedResultsController_ objectAtIndexPath:indexPath];
  [(TodoTableViewCell*)cell setDelegate:self];
  [(TodoTableViewCell*)cell setFavorite:fave];
}

#pragma mark - Map Stuff.

- (void)addAnnotationForEntity:(Entity*)entity {
  NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  STPlaceAnnotation* annotation = [[STPlaceAnnotation alloc] initWithLatitude:latitude
                                                                    longitude:longitude];  
  annotation.entityObject = entity;
  [mapView_ addAnnotation:annotation];
  [annotation release];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  if (!self.view.superview)
    return;

  userPannedMap_ = NO;
  [self.stampFilterBar.searchField resignFirstResponder];
  self.tableView.scrollEnabled = NO;
  self.fetchedResultsController.fetchRequest.predicate = [NSPredicate predicateWithFormat:@"entityObject != NIL"];

  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
  NSArray* favoritesArray = [sectionInfo objects];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     mapView_.showsUserLocation = YES;
                     for (Favorite* f in favoritesArray) {
                       if (!f.entityObject.coordinates)
                         continue;
                       [self addAnnotationForEntity:f.entityObject];
                     }
                   }];
}

- (void)listButtonWasPressed:(NSNotification*)notification {
  if (!self.view.superview)
    return;

  self.tableView.scrollEnabled = YES;
  [self filterFavorites];
  [mapView_ removeAnnotations:mapView_.annotations];
  [UIView animateWithDuration:0.5
                   animations:^{ mapView_.alpha = 0.0; }
                   completion:^(BOOL finished) { mapView_.showsUserLocation = NO; }];
}

- (void)mapDisclosureTapped:(id)sender {
  UIButton* disclosureButton = sender;
  UIView* view = [disclosureButton superview];
  while (view && ![view isMemberOfClass:[MKPinAnnotationView class]])
    view = [view superview];
  
  if (!view)
    return;
  
  STPlaceAnnotation* annotation = (STPlaceAnnotation*)[(MKPinAnnotationView*)view annotation];
  UIViewController* detailViewController = [Util detailViewControllerForEntity:annotation.entityObject];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
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
  pinView.pinColor = MKPinAnnotationColorRed;
  pinView.canShowCallout = YES;
  return pinView;
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
  indexPath = [NSIndexPath indexPathForRow:(indexPath.row + 1) inSection:0];
  newIndexPath = [NSIndexPath indexPathForRow:(newIndexPath.row + 1) inSection:0];

  UITableView* tableView = self.tableView;
  
  switch(type) {
    case NSFetchedResultsChangeInsert:
      [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath] withRowAnimation:UITableViewRowAnimationNone];
      break;
      
    case NSFetchedResultsChangeDelete:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationMiddle];
      break;
      
    case NSFetchedResultsChangeUpdate: {
      NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
      [self configureCell:[tableView cellForRowAtIndexPath:indexPath] atIndexPath:offsetIndexPath];
      break;
    }

    case NSFetchedResultsChangeMove:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
      [tableView reloadSections:[NSIndexSet indexSetWithIndex:newIndexPath.section] withRowAnimation:UITableViewRowAnimationNone];
      break;
  }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView endUpdates];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  return [sectionInfo numberOfObjects] + 1;
}

- (float)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0)
    return 64.0;
  else 
    return 82.0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                                    reuseIdentifier:nil] autorelease];
    UIImage* image = [UIImage imageNamed:@"icon_addToDo_button"];
    UIImage* highlighted = [Util whiteMaskedImageUsingImage:image];
    UIImageView* addTodoImageView = [[UIImageView alloc] initWithImage:image
                                                      highlightedImage:highlighted];
    addTodoImageView.frame = CGRectOffset(addTodoImageView.frame, 15, 21);
    [cell.contentView addSubview:addTodoImageView];
    [addTodoImageView release];
  
    UILabel* addLabel = [[UILabel alloc] initWithFrame:CGRectZero];
    addLabel.text = @"Add a to-do";
    addLabel.textColor = [UIColor stampedLightGrayColor];
    addLabel.highlightedTextColor = [UIColor whiteColor];
    addLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    [addLabel sizeToFit];
    addLabel.frame = CGRectOffset(addLabel.frame, CGRectGetMaxX(addTodoImageView.frame) + 22, 22);
    [cell.contentView addSubview:addLabel];
    [addLabel release];

    return cell;
  }

  static NSString* CellIdentifier = @"Cell";

  TodoTableViewCell* cell = (TodoTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[TodoTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
  [self configureCell:cell atIndexPath:offsetIndexPath];

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    [self.delegate displaySearchEntities];
    return;
  }

  NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
  Favorite* fave = [fetchedResultsController_ objectAtIndexPath:offsetIndexPath];
  
  UIViewController* detailViewController = [Util detailViewControllerForEntity:fave.entityObject];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
}

- (BOOL)tableView:(UITableView*)tableView canEditRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) 
    return NO;

  return YES;
}

- (void)tableView:(UITableView*)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath*)indexPath {
  // If row is deleted, remove it from the datastore.
  if (editingStyle == UITableViewCellEditingStyleDelete) {
    NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
    Favorite* fave = [fetchedResultsController_ objectAtIndexPath:offsetIndexPath];

    NSString* entityID = fave.entityObject.entityID;
    fave.entityObject.favorite = nil;
    fave.entityObject = nil;
    fave.stamp.isFavorited = [NSNumber numberWithBool:NO];
    [Favorite.managedObjectContext deleteObject:fave];
    
    [self removeFavoriteWithEntityID:entityID];    
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  Favorite* oldestFavoriteInBatch = objects.lastObject;
  if (oldestFavoriteInBatch.created) {
    [[NSUserDefaults standardUserDefaults] setObject:oldestFavoriteInBatch.created
                                              forKey:@"FavoritesOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  if (objects.count < 10) {
    // Grab latest favorite.
    NSFetchRequest* request = [Favorite fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setFetchLimit:1];
    Favorite* latestFavorite = [Favorite objectWithFetchRequest:request];
    
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"FavoritesOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] setObject:latestFavorite.created
                                              forKey:@"FavoriteLatestCreated"];
    NSDate* now = [NSDate date];
    [[NSUserDefaults standardUserDefaults] setObject:now forKey:@"TodoLastUpdatedAt"];
    [[NSUserDefaults standardUserDefaults] synchronize];
    [self updateLastUpdatedTo:now];
    [self setIsLoading:NO];
  } else {
    [self loadFavoritesFromNetwork];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
} 

- (void)objectLoaderDidLoadUnexpectedResponse:(RKObjectLoader*)objectLoader {
  if (objectLoader.response.isNotFound)
    return;

  [[Alerts alertWithTemplate:AlertTemplateDefault] show];
}

#pragma mark - TodoTableViewCellDelegate Methods.

- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldStampEntity:(Entity*)entity {
  CreateStampViewController* detailViewController = [[CreateStampViewController alloc] initWithEntityObject:entity];
  
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldShowStamp:(Stamp*)stamp {
  if (!stamp)
    return;
  
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query {
  self.searchQuery = query;
  selectedFilterType_ = filterType;
  [self filterFavorites];
  
  [self.tableView reloadData];
}

#pragma mark - Filter/Search stuff.

- (void)filterFavorites {
  NSMutableArray* predicates = [NSMutableArray array];
  [predicates addObject:[NSPredicate predicateWithFormat:@"entityObject != NIL"]];
  
  if (searchQuery_.length) {
    NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;
      
      NSPredicate* p = [NSPredicate predicateWithFormat:
                        @"(entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@)", term, term];
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
    [predicates addObject:[NSPredicate predicateWithFormat:@"entityObject.category == %@", filterString]];
  
  self.fetchedResultsController.fetchRequest.predicate = [NSCompoundPredicate andPredicateWithSubpredicates:predicates];
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
}

#pragma mark - Custom methods.

- (void)loadFavoritesFromNetwork {
  [self setIsLoading:YES];

  NSTimeInterval latestTimestamp = 0;
  NSDate* lastUpdated = [[NSUserDefaults standardUserDefaults] objectForKey:@"FavoriteLatestCreated"];
  if (lastUpdated)
    latestTimestamp = lastUpdated.timeIntervalSince1970;

  NSString* latestTimestampString = [NSString stringWithFormat:@"%.0f", latestTimestamp];
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:latestTimestampString, @"since", nil];
  NSDate* oldestTimeInBatch = [[NSUserDefaults standardUserDefaults] objectForKey:@"FavoritesOldestTimestampInBatch"];
  if (oldestTimeInBatch && oldestTimeInBatch.timeIntervalSince1970 > 0) {
    NSString* oldestTimeInBatchString = [NSString stringWithFormat:@"%.0f", oldestTimeInBatch.timeIntervalSince1970];
    [params setObject:oldestTimeInBatchString forKey:@"before"];
  }

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kShowFavoritesPath
                                                                    delegate:self];
  objectLoader.objectMapping = favoriteMapping;
  objectLoader.params = params;
  [objectLoader send];
}

- (void)loadFavoritesFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Favorite fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:[NSPredicate predicateWithFormat:@"entityObject != NIL"]];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Favorite managedObjectContext]
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

- (void)removeFavoriteWithEntityID:(NSString*)entityID {
  NSString* path = kRemoveFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:entityID, @"entity_id", nil];
  [objectLoader send];
}

@end
