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

static NSString* const kFriendsPath = @"/temp/friends.json";
static NSString* const kFollowersPath = @"/temp/followers.json";
static const NSInteger kFriendsSection = 0;
static const NSInteger kFollowersSection = 1;

@interface PeopleViewController ()
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)topViewTapped:(UITapGestureRecognizer*)recognizer;
- (void)loadFriendsAndFollowersFromNetwork;

@property (nonatomic, copy) NSArray* followersArray;
@property (nonatomic, copy) NSArray* friendsArray;
@end

@implementation PeopleViewController

@synthesize currentUserView = currentUserView_;
@synthesize userStampImageView = userStampImageView_;
@synthesize userFullNameLabel = userFullNameLabel_;
@synthesize userScreenNameLabel = userScreenNameLabel_;
@synthesize addFriendsButton = addFriendsButton_;
@synthesize followersArray = followersArray_;
@synthesize friendsArray = friendsArray_;

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
  UITapGestureRecognizer* recognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(topViewTapped:)];
  [userScreenNameLabel_.superview addGestureRecognizer:recognizer];
  [recognizer release];
  [self currentUserUpdated:nil];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
  self.followersArray = nil;
  self.friendsArray = nil;
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
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    [self setIsLoading:NO];
    return;
  }
  [self loadFriendsAndFollowersFromNetwork];
}

- (void)currentUserUpdated:(NSNotification*)notification {
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser)
    return;
  currentUserView_.imageURL = currentUser.profileImageURL;
  userStampImageView_.image = currentUser.stampImage;
  userScreenNameLabel_.text = currentUser.screenName;
  userFullNameLabel_.text = [NSString stringWithFormat:@"%@ %@", currentUser.firstName, currentUser.lastName];
  [self loadFriendsAndFollowersFromNetwork];
}

- (void)loadFriendsAndFollowersFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  NSString* authToken = [AccountManager sharedManager].authToken.accessToken;
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:authToken, @"oauth_token", userID, @"user_id", nil];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  [objectManager loadObjectsAtResourcePath:[kFriendsPath appendQueryParams:params]
                             objectMapping:userMapping
                                  delegate:self];
  [objectManager loadObjectsAtResourcePath:[kFollowersPath appendQueryParams:params]
                             objectMapping:userMapping
                                  delegate:self];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"PeopleLastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];

	if ([objectLoader.resourcePath rangeOfString:kFriendsPath].location != NSNotFound) {
    self.friendsArray = nil;
    self.friendsArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"firstName" ascending:YES]]];
  } else if ([objectLoader.resourcePath rangeOfString:kFollowersPath].location != NSNotFound) {
    self.followersArray = nil;
    self.followersArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"firstName" ascending:YES]]];
  }

  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadFriendsAndFollowersFromNetwork];
    return;
  }
  
  [self setIsLoading:NO];
}

#pragma mark - Table view data source.

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  // Two. Followers and following.
  return 2;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  if (section == kFollowersSection)
    return self.followersArray.count;
  if (section == kFriendsSection)
    return self.friendsArray.count;
  
  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  NSArray* list = indexPath.section == kFriendsSection ? self.friendsArray : self.followersArray;
  cell.user = [list objectAtIndex:indexPath.row];

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
      [NSString stringWithFormat:@"%u", section == kFriendsSection ? self.friendsArray.count : self.followersArray.count];
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  NSArray* list = indexPath.section == kFriendsSection ? self.friendsArray : self.followersArray;
  profileViewController.user = [list objectAtIndex:indexPath.row];
  
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - Custom methods.

- (void)topViewTapped:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = [AccountManager sharedManager].currentUser;
  
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

@end
