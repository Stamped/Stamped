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
#import "FindFriendsViewController.h"
#import "STSectionHeaderView.h"
#import "STNavigationBar.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"
#import "SettingsViewController.h"

static NSString* const kFriendsPath = @"/temp/friends.json";

@interface PeopleViewController ()
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)topViewTapped:(UITapGestureRecognizer*)recognizer;
- (void)loadFriendsFromNetwork;
- (UIButton*)settingsButton;
- (void)settingsButtonPressed:(id)sender;

@property (nonatomic, copy) NSArray* friendsArray;
@end

@implementation PeopleViewController

@synthesize currentUserView = currentUserView_;
@synthesize userStampImageView = userStampImageView_;
@synthesize userFullNameLabel = userFullNameLabel_;
@synthesize userScreenNameLabel = userScreenNameLabel_;
@synthesize addFriendsButton = addFriendsButton_;
@synthesize friendsArray = friendsArray_;
@synthesize settingsNavigationController = settingsNavigationController_;

- (void)dealloc {
  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
  self.friendsArray = nil;
  self.settingsNavigationController = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [self.settingsButton addTarget:self 
                          action:@selector(settingsButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
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
  if ([AccountManager sharedManager].currentUser)
    [self loadFriendsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [self.settingsButton removeTarget:self
                             action:@selector(settingsButtonPressed:)
                   forControlEvents:UIControlEventTouchUpInside];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
  self.friendsArray = nil;
  self.settingsNavigationController = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  if (delegate.navigationController.navigationBarHidden)
    [delegate.navigationController setNavigationBarHidden:NO animated:YES];

  [self loadFriendsFromNetwork];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  self.settingsButton.hidden = NO;
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  self.settingsButton.hidden = YES;
  [super viewDidDisappear:animated];
}

- (void)userPulledToReload {
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    [self setIsLoading:NO];
    return;
  }
  [self loadFriendsFromNetwork];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadFriendsFromNetwork];
}

- (void)currentUserUpdated:(NSNotification*)notification {
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser)
    return;
  currentUserView_.imageURL = currentUser.profileImageURL;
  userStampImageView_.image = currentUser.stampImage;
  userScreenNameLabel_.text = currentUser.screenName;
  userFullNameLabel_.text = currentUser.name;
}

- (void)loadFriendsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kFriendsPath delegate:self];
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"user_id", nil];
  [objectLoader send];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	if ([objectLoader.resourcePath rangeOfString:kFriendsPath].location != NSNotFound) {
    self.friendsArray = nil;
    self.friendsArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"name" ascending:YES]]];
  }
  [self.tableView reloadData];
  self.tableView.contentOffset = scrollPosition_;
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadFriendsFromNetwork];
    return;
  }
  
  [self setIsLoading:NO];
}

#pragma mark - Table view data source.

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (friendsArray_ != nil)
    return self.friendsArray.count + 1;  // One more for adding friends.

  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0 && friendsArray_ != nil) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                                    reuseIdentifier:nil] autorelease];
    UIImageView* addFriendsImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"button_addFriends"]];
    addFriendsImageView.center = cell.contentView.center;
    addFriendsImageView.frame = CGRectOffset(addFriendsImageView.frame, 0, 3);
    [cell addSubview:addFriendsImageView];
    [addFriendsImageView release];
    return cell;
  }
  
  static NSString* CellIdentifier = @"Cell";
  
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.user = [self.friendsArray objectAtIndex:indexPath.row - 1];

  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  view.leftLabel.text = @"Following";
  view.rightLabel.text = [NSString stringWithFormat:@"%u", self.friendsArray.count];
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];

  if (indexPath.row == 0) {
    FindFriendsViewController* vc = [[FindFriendsViewController alloc] initWithFindSource:FindFriendsFromContacts];
    vc.followedUsers = [NSMutableArray arrayWithArray:self.friendsArray];
    [delegate.navigationController pushViewController:vc animated:YES];
    [vc release];
    return;
  }
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = [self.friendsArray objectAtIndex:(indexPath.row - 1)];
  
  [delegate.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - Custom methods.

- (void)settingsButtonPressed:(id)sender {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController presentModalViewController:settingsNavigationController_ animated:YES];
}

- (UIButton*)settingsButton {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  return navBar.settingsButton;
}

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
