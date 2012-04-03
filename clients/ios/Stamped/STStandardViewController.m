//
//  ActivityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STStandardViewController.h"

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
#import "WebViewController.h"
#import "Util.h"

static NSString* const kActivityLookupPath = @"/activity/show.json";

@interface STStandardViewController ()
- (void)loadEventsFromNetwork;

@end

@implementation STStandardViewController

@dynamic shelfView;

#pragma mark - View lifecycle

- (void)dealloc {
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  
  [self.tableView reloadData];
  [self loadEventsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self updateLastUpdatedTo:[NSDate date]];
}

- (void)finishLoading {
  NSDate* now = [NSDate date];
  [self updateLastUpdatedTo:now];
  [self setIsLoading:NO];
  [self.tableView reloadData];
}

- (void)loadEventsFromNetwork {
  [self setIsLoading:YES];
  [self performSelector:@selector(finishLoading) withObject:nil afterDelay:1];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  return nil;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  return 55.0;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
}

#pragma mark - STTableViewController methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadEventsFromNetwork];
  [[NSNotificationCenter defaultCenter] postNotificationName:kAppShouldReloadInboxPane object:nil];
}

- (void)reloadData {
  NSLog(@"reloading data");
  // Reload the view if needed.
  [self view];
  [self loadEventsFromNetwork];
}

@end
