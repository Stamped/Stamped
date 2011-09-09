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
#import "Comment.h"
#import "Notifications.h"
#import "Event.h"
#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"

static NSString* const kActivityLookupPath = @"/temp/activity.json";

@interface ActivityViewController ()
- (void)loadEventsFromDataStore;
- (void)loadEventsFromNetwork;
@property (nonatomic, copy) NSArray* eventsArray;
@end

@implementation ActivityViewController

@synthesize eventsArray = eventsArray_;

#pragma mark - View lifecycle

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.eventsArray = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadEventsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.eventsArray = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self loadEventsFromDataStore];
}

- (void)loadEventsFromDataStore {
	NSFetchRequest* request = [Event fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  NSArray* results = [Event objectsWithFetchRequest:request];
  if (self.eventsArray) {
    NSUInteger newItemCount = results.count - self.eventsArray.count;
    if (newItemCount > 0) {
      [[NSNotificationCenter defaultCenter]
          postNotificationName:kNewsItemCountHasChangedNotification 
          object:[NSNumber numberWithUnsignedInteger:newItemCount]];
    }
  }
  self.eventsArray = nil;
	self.eventsArray = results;
  [self.tableView reloadData];
  self.tableView.contentOffset = scrollPosition_;
}

- (void)loadEventsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* eventMapping = [objectManager.mappingProvider mappingForKeyPath:@"Event"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kActivityLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = eventMapping;
  [objectLoader send];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return [eventsArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [eventsArray_ objectAtIndex:indexPath.row];
  NSString* reuseIdentifier = @"CommentIdentifier";
  if ([event.genre isEqualToString:@"restamp"])
    reuseIdentifier = @"RestampIdentifier";

  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];
  if (cell == nil) {
    if ([reuseIdentifier isEqualToString:@"RestampIdentifier"]) {
      cell = [[[ActivityCreditTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    } else {
      cell = [[[ActivityCommentTableViewCell alloc] initWithReuseIdentifier:reuseIdentifier] autorelease];
    }
  }
  if ([cell respondsToSelector:@selector(setEvent:)])
    [(id)cell setEvent:event];

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  if ([cell isMemberOfClass:[ActivityCommentTableViewCell class]]) {
    cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  } else {
    cell.backgroundColor = [UIColor whiteColor];
  }
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [eventsArray_ objectAtIndex:indexPath.row];
  if ([event.genre isEqualToString:@"comment"] ||
      [event.genre isEqualToString:@"reply"] ||
      [event.genre isEqualToString:@"mention"]) {
    CGSize stringSize = [event.comment.blurb sizeWithFont:[UIFont fontWithName:@"Helvetica" size:12]
                                        constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                            lineBreakMode:UILineBreakModeWordWrap];
    return fmaxf(60.0, stringSize.height + 40);
  }

  return 63.0;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Event* event = [eventsArray_ objectAtIndex:indexPath.row];
  if (!event)
    return;

  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithStamp:event.stamp];

  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  [[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"ActivityLastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
	[self loadEventsFromDataStore];
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
