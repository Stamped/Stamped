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

static NSString* const kUserStampsPath = @"/collections/user.json";

@interface StampListViewController ()
- (void)showMapView;
- (void)showListView;
- (void)loadStampsFromNetwork;
- (void)loadStampsFromDataStore;
- (void)filterStamps;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;

@property (nonatomic, retain) STMapViewController* mapViewController;
@property (nonatomic, assign) BOOL mapViewShown;
@property (nonatomic, retain) NSDate* oldestInBatch;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@end

@implementation StampListViewController

@synthesize listView = listView_;
@synthesize mapViewController = mapViewController_;
@synthesize mapViewShown = mapViewShown_;
@synthesize stampsAreTemporary = stampsAreTemporary_;
@synthesize user = user_;
@synthesize oldestInBatch = oldestInBatch_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize fetchedResultsController = fetchedResultsController_;

- (id)init {
  self = [self initWithNibName:@"StampListViewController" bundle:nil];
  if (self) {
    self.disableReload = YES;
    mapViewController_ = [[STMapViewController alloc] init];
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
  self.listView = nil;
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
    [self.mapViewController view];
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
  self.listView = nil;
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
    case StampFilterTypeNone:
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
  mapViewController_.user = user_;
  [mapViewController_ reset];
  [mapViewController_ view];
  mapViewController_.source = STMapViewControllerSourceUser;
  [mapViewController_ viewWillAppear:YES];
  mapViewController_.view.hidden = NO;
  [UIView transitionFromView:listView_
                      toView:mapViewController_.view
                    duration:0.75
                     options:UIViewAnimationOptionTransitionFlipFromRight
                  completion:^(BOOL finished) {
                    [self viewDidDisappear:YES];
                    [mapViewController_ viewDidAppear:YES];
                    mapViewShown_ = YES;
                  }];
}

- (void)showListView {
  [self.view insertSubview:listView_ atIndex:0];
  [mapViewController_ viewWillDisappear:YES];
  [UIView transitionFromView:mapViewController_.view
                      toView:listView_
                    duration:0.75
                     options:(UIViewAnimationOptionTransitionFlipFromLeft | UIViewAnimationOptionShowHideTransitionViews)
                  completion:^(BOOL finished) {
                    [mapViewController_ viewDidDisappear:YES];
                    mapViewShown_ = NO;
                  }];
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
