//
//  ActivityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "ActivityCommentTableViewCell.h"
#import "ActivityCreditTableViewCell.h"
#import "ActivityFriendTableViewCell.h"
#import "ActivityLikeTableViewCell.h"
#import "ActivityTodoTableViewCell.h"
#import "ActivityFollowTableViewCell.h"
#import "ActivityGenericTableViewCell.h"
#import "ProfileViewController.h"
#import "Comment.h"
#import "Notifications.h"
#import "Event.h"
#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"

static NSString* const kActivityLookupPath = @"/activity/show.json";

@interface ActivityViewController ()
- (void)loadEventsFromDataStore;
- (void)loadEventsFromNetwork;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)appDidBecomeActive:(NSNotification*)notification;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@property (nonatomic, assign) NSUInteger numRows;
@end

@implementation ActivityViewController

@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize numRows = numRows_;

#pragma mark - View lifecycle

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:self.view.bounds];
  scrollView.scrollsToTop = NO;
  UIImageView* emptyView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"empty_news"]];
  [scrollView addSubview:emptyView];
  [emptyView release];
  [self.view insertSubview:scrollView atIndex:0];
  scrollView.delegate = self;
  scrollView.alwaysBounceVertical = YES;
  scrollView.contentSize = self.view.frame.size;
  [scrollView release];

  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(appDidBecomeActive:)
                                               name:UIApplicationDidBecomeActiveNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(reloadData)
                                               name:kAppShouldReloadNewsPane
                                             object:nil];
  [self loadEventsFromDataStore];
  [self.tableView reloadData];
  [self loadEventsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"ActivityLastUpdatedAt"]];
}

- (void)loadEventsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Event fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    NSArray* genres = [NSArray arrayWithObjects:@"generic", @"comment", @"reply", @"mention", @"like", @"favorite", @"follower", @"friend", @"restamp", nil];
    NSMutableArray* preds = [NSMutableArray array];
    for (NSString* genre in genres)
      [preds addObject:[NSString stringWithFormat:@"genre == '%@'", genre]];

    [request setPredicate:[NSPredicate predicateWithFormat:[preds componentsJoinedByString:@" OR "]]];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Event managedObjectContext]
                                              sectionNameKeyPath:nil
                                                       cacheName:@"ActivityItems"];
    self.fetchedResultsController = fetchedResultsController;
    fetchedResultsController.delegate = self;
    [fetchedResultsController release];
  }
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
  
  NSUInteger numObjects = [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects];
  self.tableView.hidden = (numObjects == 0);
}

- (void)loadEventsFromNetwork {
  [self setIsLoading:YES];
  
  NSTimeInterval latestTimestamp = 0;
  NSDate* lastUpdated = [[NSUserDefaults standardUserDefaults] objectForKey:@"EventLatestCreated"];
  if (lastUpdated)
    latestTimestamp = lastUpdated.timeIntervalSince1970;

  NSString* latestTimestampString = [NSString stringWithFormat:@"%.0f", latestTimestamp];
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:latestTimestampString, @"since", nil];
  NSDate* oldestTimeInBatch = [[NSUserDefaults standardUserDefaults] objectForKey:@"EventsOldestTimestampInBatch"];
  if (oldestTimeInBatch && oldestTimeInBatch.timeIntervalSince1970 > 0) {
    NSString* oldestTimeInBatchString = [NSString stringWithFormat:@"%.0f", oldestTimeInBatch.timeIntervalSince1970];
    [params setObject:oldestTimeInBatchString forKey:@"before"];
  }

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* eventMapping = [objectManager.mappingProvider mappingForKeyPath:@"Event"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kActivityLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = eventMapping;
  objectLoader.params = params;
  [objectLoader send];
}

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerWillChangeContent:(NSFetchedResultsController*)controller {
  numRows_ = MAX(numRows_, [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects]);
}

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView reloadData];
  NSUInteger numObjects = [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects];
  if (numObjects > numRows_) {
    [[NSNotificationCenter defaultCenter]
        postNotificationName:kNewsItemCountHasChangedNotification
                      object:[NSNumber numberWithUnsignedInteger:numObjects - numRows_]];
  }
  self.tableView.hidden = (numObjects == 0);

  numRows_ = numObjects;
}

- (void)appDidBecomeActive:(NSNotification*)notification {
  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  return [sectionInfo numberOfObjects];
}

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  Event* event = [fetchedResultsController_ objectAtIndexPath:indexPath];
  if ([cell respondsToSelector:@selector(setEvent:)])
    [(id)cell setEvent:event];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [fetchedResultsController_ objectAtIndexPath:indexPath];
  NSString* reuseIdentifier = @"CommentIdentifier";
  if ([event.genre isEqualToString:@"restamp"]) {
    reuseIdentifier = @"RestampIdentifier";
  } else if ([event.genre isEqualToString:@"like"]) {
    reuseIdentifier = @"LikeIdentifier";
  } else if ([event.genre isEqualToString:@"favorite"]) {
    reuseIdentifier = @"TodoIdentifier";
  } else if ([event.genre isEqualToString:@"follower"]) {
    reuseIdentifier = @"FollowIdentifier";
  } else if ([event.genre isEqualToString:@"friend"]) {
    reuseIdentifier = @"FriendIdentifier";
  } else if ([event.genre isEqualToString:@"generic"]) {
    reuseIdentifier = @"GenericIdentifier";
  }

  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];
  if (cell == nil) {
    if ([reuseIdentifier isEqualToString:@"RestampIdentifier"]) {
      cell = [[[ActivityCreditTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"CommentIdentifier"]) {
      cell = [[[ActivityCommentTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"LikeIdentifier"]) {
      cell = [[[ActivityLikeTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"TodoIdentifier"]) {
      cell = [[[ActivityTodoTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"FollowIdentifier"]) {
      cell = [[[ActivityFollowTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"FriendIdentifier"]) {
      cell = [[[ActivityFriendTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else if ([reuseIdentifier isEqualToString:@"GenericIdentifier"]) {
      cell = [[[ActivityGenericTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    }
  }

  [self configureCell:cell atIndexPath:indexPath];

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  if ([cell isMemberOfClass:[ActivityCreditTableViewCell class]]) {
    cell.backgroundColor = [UIColor whiteColor];
  } else {
    cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  }
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [fetchedResultsController_ objectAtIndexPath:indexPath];
  if ([event.genre isEqualToString:@"comment"] ||
      [event.genre isEqualToString:@"reply"] ||
      [event.genre isEqualToString:@"mention"]) {
    CGSize stringSize = [event.blurb sizeWithFont:[UIFont fontWithName:@"Helvetica" size:12]
                                constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                    lineBreakMode:UILineBreakModeWordWrap];
    return (stringSize.height + 57);
  } else if ([event.genre isEqualToString:@"restamp"]) {
    return 80.0;
  } else if ([event.genre isEqualToString:@"friend"]) {
    NSString* full = [NSString stringWithFormat:@"%@ just joined Stamped as %@", event.subject, event.user.screenName];
    CGSize stringSize = [full sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]
                         constrainedToSize:CGSizeMake(210, MAXFLOAT)
                             lineBreakMode:UILineBreakModeWordWrap];
    return fmaxf(52.0, stringSize.height + 42);
  }

  return 55.0;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [fetchedResultsController_ objectAtIndexPath:indexPath];

  if (!event)
    return;

  UIViewController* detailViewController = nil;
  if ([event.genre isEqualToString:@"follower"] || [event.genre isEqualToString:@"friend"]) {
    detailViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
    [(ProfileViewController*)detailViewController setUser:event.user];
  } else {
    detailViewController = [[StampDetailViewController alloc] initWithStamp:event.stamp];
  }
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  Event* oldestEventInBatch = objects.lastObject;
  if (oldestEventInBatch.created) {
    [[NSUserDefaults standardUserDefaults] setObject:oldestEventInBatch.created
                                              forKey:@"EventsOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  // No need to download every event on the first run.
  if (objects.count < 10 || ![[NSUserDefaults standardUserDefaults] boolForKey:@"ActivityHasBeenLoadedOnce"]) {
    // Grab latest event.
    NSFetchRequest* request = [Event fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setFetchLimit:1];
    Event* latestEvent = [Event objectWithFetchRequest:request];
    
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"ActivityHasBeenLoadedOnce"];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"EventsOldestTimestampInBatch"];
    [[NSUserDefaults standardUserDefaults] setObject:latestEvent.created
                                              forKey:@"EventLatestCreated"];
    NSDate* now = [NSDate date];
    [[NSUserDefaults standardUserDefaults] setObject:now forKey:@"ActivityLastUpdatedAt"];
    [[NSUserDefaults standardUserDefaults] synchronize];
    [self updateLastUpdatedTo:now];
    [self setIsLoading:NO];
  } else {
    [self loadEventsFromNetwork];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadEventsFromNetwork];
    return;
  }
  [self setIsLoading:NO];
}

#pragma mark - STTableViewController methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadEventsFromNetwork];
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadInboxPane object:nil];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadEventsFromNetwork];
}

@end
