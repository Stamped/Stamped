//
//  ActivityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "ActivityCommentTableViewCell.h"
#import "ActivityCreditTableViewCell.h"
#import "ActivityLikeTableViewCell.h"
#import "ActivityTodoTableViewCell.h"
#import "ActivityFollowTableViewCell.h"
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
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@property (nonatomic, assign) NSUInteger numRows;
@end

@implementation ActivityViewController

@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize numRows = numRows_;

#pragma mark - View lifecycle

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadEventsFromDataStore];
  [self loadEventsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)loadEventsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Event fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
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
}

- (void)loadEventsFromNetwork {
  [self setIsLoading:YES];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* eventMapping = [objectManager.mappingProvider mappingForKeyPath:@"Event"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kActivityLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = eventMapping;
  [objectLoader send];
}

#pragma mark - NSFetchedResultsControllerDelegate method.

- (void)controllerWillChangeContent:(NSFetchedResultsController*)controller {
  numRows_ = [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects];
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
      [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath] withRowAnimation:UITableViewRowAnimationFade];
      break;
      
    case NSFetchedResultsChangeDelete:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
      break;
      
    case NSFetchedResultsChangeUpdate:
      [self configureCell:[tableView cellForRowAtIndexPath:indexPath] atIndexPath:indexPath];
      break;
      
    case NSFetchedResultsChangeMove:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
      [tableView reloadSections:[NSIndexSet indexSetWithIndex:newIndexPath.section] withRowAnimation:UITableViewRowAnimationFade];
      break;
  }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView endUpdates];
  NSUInteger numNewRows = [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects] - numRows_;
  if (numNewRows > 0) {
    [[NSNotificationCenter defaultCenter]
        postNotificationName:kNewsItemCountHasChangedNotification
                      object:[NSNumber numberWithUnsignedInteger:numNewRows]];
  }

  numRows_ = [[[fetchedResultsController_ sections] objectAtIndex:0] numberOfObjects];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

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
    return fmaxf(52.0, stringSize.height + 57);
  } else if ([event.genre isEqualToString:@"restamp"]) {
    return 80.0;
  }

  return 55.0;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [fetchedResultsController_ objectAtIndexPath:indexPath];

  if (!event)
    return;

  UIViewController* detailViewController = nil;
  if ([event.genre isEqualToString:@"follower"]) {
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
  [[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"ActivityLastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
  [self setIsLoading:NO];
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

#pragma mark - STReloadableTableView methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadEventsFromNetwork];
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadAllPanes
                                                      object:self];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadEventsFromNetwork];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [super scrollViewDidScroll:scrollView];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  [super scrollViewDidEndDragging:scrollView willDecelerate:decelerate];
}


@end
