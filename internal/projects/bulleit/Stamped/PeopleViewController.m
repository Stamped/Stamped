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
#import "Notifications.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"
#import "SettingsViewController.h"

static NSString* const kFriendsPath = @"/temp/friends.json";

@interface PeopleViewController ()
- (void)loadFriendsFromNetwork;
- (void)loadFriendsFromDataStore;
- (void)settingsButtonPressed:(NSNotification*)notification;
- (void)userProfileHasChanged:(NSNotification*)notification;

@property (nonatomic, copy) NSArray* friendsArray;
@end

@implementation PeopleViewController

@synthesize friendsArray = friendsArray_;
@synthesize settingsNavigationController = settingsNavigationController_;
@synthesize findFriendsNavigationController = findFriendsNavigationController_;

- (void)dealloc {
  self.friendsArray = nil;
  self.settingsNavigationController = nil;
  self.findFriendsNavigationController = nil;
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(settingsButtonPressed:)
                                               name:kSettingsButtonPressedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(userProfileHasChanged:)
                                               name:kUserProfileHasChangedNotification
                                             object:nil];
  if ([AccountManager sharedManager].currentUser) {
    [self loadFriendsFromNetwork];
    [self loadFriendsFromDataStore];
  }
  
  self.hasHeaders = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.friendsArray = nil;
  self.settingsNavigationController = nil;
  self.findFriendsNavigationController = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  
  [self loadFriendsFromDataStore];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  if (delegate.navigationController.navigationBarHidden)
    [delegate.navigationController setNavigationBarHidden:NO animated:YES];

  if (!friendsArray_.count)
    [self loadFriendsFromNetwork];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setSettingsButtonShown:YES];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"PeopleLastUpdatedAt"]];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setSettingsButtonShown:NO];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)userPulledToReload {
  [self loadFriendsFromNetwork];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadFriendsFromNetwork];
}

- (void)loadFriendsFromDataStore {
  NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                               ascending:YES 
                                                                selector:@selector(localizedCaseInsensitiveCompare:)];
  User* currentUser = [AccountManager sharedManager].currentUser;
  self.friendsArray = [currentUser.following sortedArrayUsingDescriptors:[NSArray arrayWithObject:descriptor]];
  [self.tableView reloadData];
}

- (void)loadFriendsFromNetwork {
  [self setIsLoading:YES];
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
    User* currentUser = [AccountManager sharedManager].currentUser;
    [currentUser removeFollowing:currentUser.following];
    [currentUser addFollowing:[NSSet setWithArray:objects]];
    [User.managedObjectContext save:NULL];
    NSSortDescriptor* sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                                     ascending:YES 
                                                                      selector:@selector(localizedCaseInsensitiveCompare:)];
    self.friendsArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
  }
  [self.tableView reloadData];
  NSDate* now = [NSDate date];
  [[NSUserDefaults standardUserDefaults] setObject:now forKey:@"PeopleLastUpdatedAt"];
  [[NSUserDefaults standardUserDefaults] synchronize];
  [self updateLastUpdatedTo:now];
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
  return 2;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (section == 0)
    return 1;

  if (friendsArray_ != nil)
    return self.friendsArray.count + 1;  // One more for adding friends.

  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.section == 1 && indexPath.row == 0 && friendsArray_ != nil) {
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
  if (cell == nil)
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  
  User* user = nil;
  if (indexPath.section == 0)
    user = [AccountManager sharedManager].currentUser;
  else
    user = [self.friendsArray objectAtIndex:indexPath.row - 1];
  
  cell.user = user;

  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  if (section == 0) {
    view.leftLabel.text = @"You";
  } else if (section == 1) {
    view.leftLabel.text = @"Following";
    view.rightLabel.text = [NSString stringWithFormat:@"%u", self.friendsArray.count];
  }
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];

  if (indexPath.section == 1 && indexPath.row == 0) {
    StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
    [delegate.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
    [((FindFriendsViewController*)[findFriendsNavigationController_.viewControllers objectAtIndex:0]) didDisplayAsModal]; 
    return;
  }
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController"
                                                                                         bundle:nil];
  User* currentUser = [AccountManager sharedManager].currentUser;
  User* user = nil;
  if (indexPath.section == 0) {
    user = currentUser;
    profileViewController.stampsAreTemporary = NO;
  } else {
    user = [self.friendsArray objectAtIndex:indexPath.row - 1];
    profileViewController.stampsAreTemporary = [currentUser.following containsObject:user];
  }
  profileViewController.user = user;
  
  [delegate.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - Custom methods.

- (void)settingsButtonPressed:(NSNotification*)notification {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController presentModalViewController:settingsNavigationController_ animated:YES];
}

- (void)userProfileHasChanged:(NSNotification*)notification {
  [self.tableView reloadData];
}

@end
