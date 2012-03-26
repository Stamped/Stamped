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

#import "AccountManager.h"
#import "Entity.h"
#import "UserImageView.h"
#import "Notifications.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "STStampDetailViewController.h"
#import "Stamp.h"
#import "STNavigationBar.h"
#import "STPlaceAnnotation.h"
#import "STStampFilterBar.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static NSString* const kInboxPath = @"/collections/inbox.json";

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)filterStamps;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)userLoggedOut:(NSNotification*)notification;
- (void)appDidBecomeActive:(NSNotification*)notification;
- (void)appDidEnterBackground:(NSNotification*)notification;
- (void)managedObjectContextChanged:(NSNotification*)notification;

@property (nonatomic, assign) BOOL needToRefetch;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@property (nonatomic, retain) NSIndexPath* selectedIndexPath;

@end

@implementation InboxViewController

@synthesize needToRefetch = needToRefetch_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize selectedIndexPath = selectedIndexPath_;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {
    [[AccountManager sharedManager] addObserver:self
                                     forKeyPath:@"currentUser.following"
                                        options:(NSKeyValueObservingOptionNew | NSKeyValueObservingOptionOld)
                                        context:NULL];
  }
  return self;
}

- (void)dealloc {
  [[AccountManager sharedManager] removeObserver:self forKeyPath:@"currentUser.following"];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.searchQuery = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  self.selectedIndexPath = nil;

  [super dealloc];
}

#pragma mark - KVO

- (void)observeValueForKeyPath:(NSString*)keyPath
                      ofObject:(id)object
                        change:(NSDictionary*)change
                       context:(void*)context {
  id old = [change objectForKey:NSKeyValueChangeOldKey];
  id new = [change objectForKey:NSKeyValueChangeNewKey];
  if (old == new)
    return;

  if ([keyPath isEqualToString:@"currentUser.following"]) {
    if (new != [NSNull null])
      [self filterStamps];
  }
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
                                           selector:@selector(userLoggedOut:)
                                               name:kUserHasLoggedOutNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(managedObjectContextChanged:)
                                               name:NSManagedObjectContextObjectsDidChangeNotification
                                             object:[Entity managedObjectContext]];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(reloadData)
                                               name:kAppShouldReloadInboxPane
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(appDidBecomeActive:)
                                               name:UIApplicationDidBecomeActiveNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(appDidEnterBackground:)
                                               name:UIApplicationDidEnterBackgroundNotification
                                             object:nil];

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
  [super viewWillAppear:animated];
  User* currentUser = [AccountManager sharedManager].currentUser;
  BOOL shouldHideShelfAndTable = NO;
  if (currentUser && currentUser.numStamps.integerValue == 0 && currentUser.following.count == 0)
    shouldHideShelfAndTable = YES;

  self.tableView.hidden = shouldHideShelfAndTable;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (needToRefetch_) {
    NSError* error;
    if (![self.fetchedResultsController performFetch:&error]) {
      // Update to handle the error appropriately.
      NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
    }

    needToRefetch_ = NO;
    [self.tableView reloadData];
  }

  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"InboxLastUpdatedAt"]];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  self.selectedIndexPath = [self.tableView indexPathForSelectedRow];
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
  if (objects.count == 0)
    return;
  User* currentUser = [AccountManager sharedManager].currentUser;
  NSString* currentUserID = currentUser.userID;
  NSSet* allStampsOrCurrentUser = [objects objectsPassingTest:^BOOL(id obj, BOOL* stop) {
    if ([obj isMemberOfClass:[Stamp class]] ||
        ([obj isMemberOfClass:[User class]] && [[(User*)obj userID] isEqualToString:currentUserID])) {
      *stop = YES;
      return YES;
    }
    return NO;
  }];

  if (allStampsOrCurrentUser.count > 0) {
    needToRefetch_ = YES;
    for (id obj in allStampsOrCurrentUser) {
      if ([obj isMemberOfClass:[Stamp class]]) {
        [[obj entityObject] updateLatestStamp];
      } else {
        User* user = obj;
        NSArray* entities = [user valueForKeyPath:@"following.stamps.@distinctUnionOfSets.entityObject"];
        for (Entity* e in entities)
          [e updateLatestStamp];
      }
    }
  }
}

- (void)loadStampsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Entity fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"mostRecentStampDate" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    User* currentUser = [AccountManager sharedManager].currentUser;
    NSSet* following = currentUser.following;
    if (!following)
      following = [NSSet set];

    [request setPredicate:
        [NSPredicate predicateWithFormat:@"(SUBQUERY(stamps, $s, ($s.user IN %@ OR $s.user.userID == %@) AND $s.deleted == NO).@count != 0)", following, currentUser.userID]];
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
  if (!fetchedResultsController_)
    return;

  NSMutableArray* predicates = [NSMutableArray array];
  User* currentUser = [AccountManager sharedManager].currentUser;
  NSSet* following = currentUser.following;
  if (!following)
    following = [NSSet set];

  [predicates addObject:[NSPredicate predicateWithFormat:@"(SUBQUERY(stamps, $s, ($s.user IN %@ OR $s.user.userID == %@) AND $s.deleted == NO).@count != 0)", following, currentUser.userID]];

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
    }
    [stamp.entityObject updateLatestStamp];
  }
  
  Stamp* oldestStampInBatch = objects.lastObject;
  if (oldestStampInBatch.modified) {
    [[NSUserDefaults standardUserDefaults] setObject:oldestStampInBatch.modified
                                              forKey:@"InboxOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  for (Stamp* stamp in toDelete) {
    [Stamp.managedObjectContext deleteObject:stamp];
  }

  [Stamp.managedObjectContext save:NULL];

  if (objects.count < 10) {
    // Grab latest stamp.
    NSFetchRequest* request = [Stamp fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"modified" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
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
    User* currentUser = [AccountManager sharedManager].currentUser;
    NSSet* following = currentUser.following;
    if (!following)
      following = [NSSet set];

    sortedStamps = [sortedStamps filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"(user IN %@ OR user.userID == %@) AND deleted == NO", following, currentUser.userID]];
    stamp = [sortedStamps lastObject];
  } else {
    stamp = [entity.stamps anyObject];
  }
  
  STStampDetailViewController* vc = [[STStampDetailViewController alloc] initWithNibName:@"STStampDetailViewController" bundle:nil];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:vc animated:YES];
  [vc release];
}

#pragma mark - STTableViewController methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  // TODO(andybons): Put this somewhere nicer.
  [self.stampFilterBar reset];
  self.searchQuery = nil;
  selectedFilterType_ = StampFilterTypeNone;
  [self filterStamps];
  [self.tableView reloadData];

  [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"InboxOldestTimestampInBatch"];
  [[NSUserDefaults standardUserDefaults] synchronize];
  [self loadStampsFromNetwork];
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadNewsPane object:nil];
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

- (void)appDidBecomeActive:(NSNotification*)notification {
  [self.tableView reloadData];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"InboxLastUpdatedAt"]];
}

- (void)appDidEnterBackground:(NSNotification*)notification {

}

@end
