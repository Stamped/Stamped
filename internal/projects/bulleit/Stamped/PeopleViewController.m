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
#import "FriendshipManager.h"
#import "STSectionHeaderView.h"
#import "STNavigationBar.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "Notifications.h"
#import "ProfileViewController.h"
#import "StampedAppDelegate.h"
#import "SettingsViewController.h"
#import "Util.h"

static NSString* const kFriendIDsPath = @"/friendships/friends.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";

@interface PeopleViewController ()
- (void)loadUserDataFromNetwork;
- (void)loadFriendsFromNetwork;
- (void)loadFriendsFromDataStore;
- (void)settingsButtonPressed:(NSNotification*)notification;
- (void)userProfileHasChanged:(NSNotification*)notification;
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)updateShelf;

@property (nonatomic, retain) NSMutableArray* userIDsToBeFetched;
@property (nonatomic, copy) NSArray* friendsArray;
@end

@implementation PeopleViewController

@synthesize userIDsToBeFetched = userIDsToBeFetched_;
@synthesize friendsArray = friendsArray_;
@synthesize settingsNavigationController = settingsNavigationController_;
@synthesize findFriendsNavigationController = findFriendsNavigationController_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userIDsToBeFetched = nil;
  self.friendsArray = nil;
  self.settingsNavigationController = nil;
  self.findFriendsNavigationController = nil;
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(currentUserUpdated:)
                                               name:kCurrentUserHasUpdatedNotification
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
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
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

- (void)loadUserDataFromNetwork {
  if (!userIDsToBeFetched_ || userIDsToBeFetched_.count == 0)
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = userMapping;
  NSUInteger userIDCount = userIDsToBeFetched_.count;
  NSArray* subArray = [userIDsToBeFetched_ subarrayWithRange:NSMakeRange(0, MIN(100, userIDCount))];
  objectLoader.params = [NSDictionary dictionaryWithObject:[subArray componentsJoinedByString:@","]
                                                    forKey:@"user_ids"];
  objectLoader.method = RKRequestMethodPOST;
  [objectLoader send];
}

- (void)loadFriendsFromDataStore {
  NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                               ascending:YES 
                                                                selector:@selector(localizedCaseInsensitiveCompare:)];
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser)
    return;

  self.friendsArray = [currentUser.following sortedArrayUsingDescriptors:[NSArray arrayWithObject:descriptor]];
  [self.tableView reloadData];
}

- (void)loadFriendsFromNetwork {
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  if (!userID)
    return;

  [self setIsLoading:YES];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kFriendIDsPath
                                                               delegate:self];
  request.params = [NSDictionary dictionaryWithObject:userID forKey:@"user_id"];
  [request send];
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK) {
    [self updateShelf];
    [self setIsLoading:NO];
    return;
  }

  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser) {
    [self updateShelf];
    [self setIsLoading:NO];
    return;
  }

  if ([request.resourcePath rangeOfString:kFriendIDsPath].location != NSNotFound) {
    NSError* error = NULL;
    id responseObj = [response parsedBody:&error];
    if (error) {
      NSLog(@"Problem parsing response JSON: %@", error);
    } else {
      NSArray* followingIDs = (NSArray*)[responseObj objectForKey:@"user_ids"];
      // Which users need information fetched for them?
      NSSet* currentIDs = [currentUser.following valueForKeyPath:@"@distinctUnionOfObjects.userID"];
      if ([[NSSet setWithArray:followingIDs] isEqualToSet:currentIDs]) {
        [self updateShelf];
        [self setIsLoading:NO];
        return;
      }
      // New people that need following. Load in 100-user increments.
      self.userIDsToBeFetched = [NSMutableArray array];
      for (NSString* userID in followingIDs) {
        if (![currentIDs containsObject:userID])
          [userIDsToBeFetched_ addObject:userID];
      }
      if (userIDsToBeFetched_.count > 0) {
        [self loadUserDataFromNetwork];
      } else {
        self.userIDsToBeFetched = nil;
        [self updateShelf];
        [self setIsLoading:NO];
      }

      // Unfollowed. Remove stamps from inbox and following set.
      for (NSString* userID in currentIDs.allObjects) {
        if (![followingIDs containsObject:userID]) {
          User* userToUnFollow = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"userID == %@", userID]];
          if (userToUnFollow)
            [[FriendshipManager sharedManager] unfollowUser:userToUnFollow];
        }
      }
    }
  }
  [self updateShelf];
  [self setIsLoading:NO];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser) {
    [self updateShelf];
    [self setIsLoading:NO];
    return;
  }

  if ([objectLoader.resourcePath rangeOfString:kUserLookupPath].location != NSNotFound) {
    for (User* user in objects) {
      [currentUser addFollowingObject:user];
      [userIDsToBeFetched_ removeObject:user.userID];
    }
    if (userIDsToBeFetched_.count > 0) {
      [self loadUserDataFromNetwork];
      return;
    } else {
      self.userIDsToBeFetched = nil;
    }
  }
  self.friendsArray = nil;
  NSSortDescriptor* sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                                   ascending:YES 
                                                                    selector:@selector(localizedCaseInsensitiveCompare:)];
  self.friendsArray = [currentUser.following.allObjects sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
  [self.tableView reloadData];

  [self updateShelf];
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

- (void)updateShelf {
  NSDate* now = [NSDate date];
  [[NSUserDefaults standardUserDefaults] setObject:now forKey:@"PeopleLastUpdatedAt"];
  [[NSUserDefaults standardUserDefaults] synchronize];
  [self updateLastUpdatedTo:now];
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
    UIImage* addFriendsImage = [UIImage imageNamed:@"addFriends_profilePic"];
    UIImage* highlightedAddFriendsImage = [Util whiteMaskedImageUsingImage:addFriendsImage];
    UIImageView* addFriendsImageView = [[UIImageView alloc] initWithImage:addFriendsImage
                                                         highlightedImage:highlightedAddFriendsImage];
    addFriendsImageView.frame = CGRectOffset(addFriendsImageView.frame, 10, 5);
    [cell.contentView addSubview:addFriendsImageView];
    [addFriendsImageView release];
    UILabel* addFriendsLabel = [[UILabel alloc] initWithFrame:CGRectZero];
    addFriendsLabel.text = @"Add friends";
    addFriendsLabel.textColor = [UIColor stampedLightGrayColor];
    addFriendsLabel.highlightedTextColor = [UIColor whiteColor];
    addFriendsLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    [addFriendsLabel sizeToFit];
    addFriendsLabel.frame = CGRectOffset(addFriendsLabel.frame, CGRectGetMaxX(addFriendsImageView.frame) + 18, 15);
    [cell.contentView addSubview:addFriendsLabel];
    [addFriendsLabel release];
    UIImage* friendIcons = [UIImage imageNamed:@"addFriends_icons"];
    UIImage* highlightedFriendIcons = [Util whiteMaskedImageUsingImage:friendIcons];
    UIImageView* iconsImageView = [[UIImageView alloc] initWithImage:friendIcons
                                                    highlightedImage:highlightedFriendIcons];
    iconsImageView.frame = CGRectOffset(iconsImageView.frame, 320 - CGRectGetWidth(iconsImageView.frame) - 18, 19);
    [cell.contentView addSubview:iconsImageView];
    [iconsImageView release];
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

- (void)currentUserUpdated:(NSNotification*)notification {
  if (!friendsArray_) {
    [self loadFriendsFromNetwork];
    [self loadFriendsFromDataStore];
  }
}

@end
