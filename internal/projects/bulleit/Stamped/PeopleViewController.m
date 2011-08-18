//
//  PeopleViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "STSectionHeaderView.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"

static NSString* const kFriendsPath = @"/friendships/friends";
static NSString* const kFollowersPath = @"/friendships/friends";
static const NSInteger kFriendsSection = 0;
static const NSInteger kFollowersSection = 1;

@interface PeopleViewController ()
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)loadFriendsFromNetwork;
- (void)loadFriendsFromDataStore;

@property (nonatomic, copy) NSArray* followers;
@property (nonatomic, copy) NSArray* friends;
@end

@implementation PeopleViewController

@synthesize currentUserView = currentUserView_;
@synthesize userStampImageView = userStampImageView_;
@synthesize userFullNameLabel = userFullNameLabel_;
@synthesize userScreenNameLabel = userScreenNameLabel_;
@synthesize addFriendsButton = addFriendsButton_;
@synthesize followers = followers_;
@synthesize friends = friends_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(currentUserUpdated:)
                                               name:kCurrentUserHasUpdatedNotification
                                             object:[AccountManager sharedManager]];
  
  userScreenNameLabel_.textColor = [UIColor stampedLightGrayColor];
  userFullNameLabel_.textColor = [UIColor stampedBlackColor];
  [self currentUserUpdated:nil];
  [self loadFriendsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)userPulledToReload {
  [self setIsLoading:NO];
}

- (void)currentUserUpdated:(NSNotification*)notification {
  User* currentUser = [AccountManager sharedManager].currentUser;
  currentUserView_.imageURL = currentUser.profileImageURL;
  userStampImageView_.image = currentUser.stampImage;
  userScreenNameLabel_.text = currentUser.screenName;
  userFullNameLabel_.text = [NSString stringWithFormat:@"%@ %@", currentUser.firstName, currentUser.lastName];
}

- (void)loadFriendsFromNetwork {
  /*if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  NSString* authToken = [AccountManager sharedManager].authToken.accessToken;
  NSDictionary* params = [NSDictionary dictionaryWithObject:authToken forKey:@"oauth_token"];
  //[[RKClient sharedClient] get:kFriendsPath
  //                 queryParams:params
  //                    delegate:self];*/
}

- (void)loadFriendsFromDataStore {
  
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  // Two. Followers and following.
  return 2;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 50;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.user = [AccountManager sharedManager].currentUser;

  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)];
  view.leftLabel.text = section == kFriendsSection ? @"Following" : @"Followers";
  view.rightLabel.text =
      [NSString stringWithFormat:@"%u", section == kFriendsSection ? [friends_ count] : [followers_ count]];
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = [AccountManager sharedManager].currentUser;
  
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

@end
