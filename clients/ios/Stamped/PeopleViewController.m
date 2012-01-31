//
//  PeopleViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleViewController.h"

#import <QuartzCore/QuartzCore.h>

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
#import "STSearchField.h"
#import "StampedAppDelegate.h"
#import "SettingsViewController.h"
#import "Util.h"

static NSString* const kFriendIDsPath = @"/friendships/friends.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";
static NSString* const kStampedSearchURI = @"/users/search.json";

typedef enum PeopleSearchCorpus {
  PeopleSearchCorpusFollowing,
  PeopleSearchCorpusFollowers,
  PeopleSearchCorpusEveryone
} PeopleSearchCorpus;

@interface PeopleViewController ()
- (void)loadUserDataFromNetwork;
- (void)loadFriendsFromNetwork;
- (void)loadFriendsFromDataStore;
- (void)userProfileHasChanged:(NSNotification*)notification;
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)updateShelf;

@property (nonatomic, assign) PeopleSearchCorpus searchCorpus;
@property (nonatomic, retain) NSMutableArray* userIDsToBeFetched;
@property (nonatomic, copy) NSArray* friendsArray;
@property (nonatomic, copy) NSArray* searchResults;
@end

@implementation PeopleViewController

@synthesize searchCorpus = searchCorpus_;
@synthesize userIDsToBeFetched = userIDsToBeFetched_;
@synthesize friendsArray = friendsArray_;
@synthesize searchResults = searchResults_;
@synthesize findFriendsNavigationController = findFriendsNavigationController_;
@synthesize searchSegmentedControl = searchSegmentedControl_;
@synthesize shelfSeparator = shelfSeparator_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userIDsToBeFetched = nil;
  self.friendsArray = nil;
  self.findFriendsNavigationController = nil;
  self.searchResults = nil;
  self.searchSegmentedControl = nil;
  self.shelfSeparator = nil;
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
  if ([searchSegmentedControl_ conformsToProtocol:@protocol(UIAppearance)]) {
    NSDictionary* titleTextAttributes = [NSDictionary dictionaryWithObjectsAndKeys:(id)[UIColor stampedGrayColor], (id)UITextAttributeTextColor,
                                         (id)[UIColor whiteColor], (id)UITextAttributeTextShadowColor, 
                                         (id)[NSValue valueWithUIOffset:UIOffsetMake(0, 1)], (id)UITextAttributeTextShadowOffset,  nil];
    [searchSegmentedControl_ setTitleTextAttributes:titleTextAttributes forState:UIControlStateNormal];
    NSDictionary* selectedTextAttributes = [NSDictionary dictionaryWithObjectsAndKeys:(id)[UIColor whiteColor], (id)UITextAttributeTextColor,
                                            (id)[UIColor colorWithWhite:0.5 alpha:1.0], (id)UITextAttributeTextShadowColor,
                                            (id)[NSValue valueWithUIOffset:UIOffsetMake(0, -1)], (id)UITextAttributeTextShadowOffset,  nil];
    [searchSegmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateSelected];
    [searchSegmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateHighlighted];
    [searchSegmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateNormal | UIControlStateSelected];
  }
  self.hasHeaders = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.friendsArray = nil;
  self.searchResults = nil;
  self.findFriendsNavigationController = nil;
  self.searchSegmentedControl = nil;
  self.shelfSeparator = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  
  [self loadFriendsFromDataStore];
  if (self.navigationController.navigationBarHidden)
    [self.navigationController setNavigationBarHidden:NO animated:YES];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self updateLastUpdatedTo:[[NSUserDefaults standardUserDefaults] objectForKey:@"PeopleLastUpdatedAt"]];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
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
    addFriendsLabel.frame = CGRectOffset(addFriendsLabel.frame, CGRectGetMaxX(addFriendsImageView.frame) + 18, 16);
    [cell.contentView addSubview:addFriendsLabel];
    [addFriendsLabel release];
    UIImage* friendIcons = [UIImage imageNamed:@"addFriends_icons"];
    UIImage* highlightedFriendIcons = [Util whiteMaskedImageUsingImage:friendIcons];
    UIImageView* iconsImageView = [[UIImageView alloc] initWithImage:friendIcons
                                                    highlightedImage:highlightedFriendIcons];
    iconsImageView.frame = CGRectOffset(iconsImageView.frame, 320 - CGRectGetWidth(iconsImageView.frame) - 18, 20);
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
  return 24;
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
  if (indexPath.section == 1 && indexPath.row == 0) {
    [self.navigationController presentModalViewController:findFriendsNavigationController_ animated:YES];
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
  
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [super textFieldDidBeginEditing:textField];
  CGFloat offset = -44;
  NSArray* views = [NSArray arrayWithObjects:self.searchField, self.cancelButton, self.reloadLabel, self.lastUpdatedLabel, self.arrowImageView, self.spinnerView, nil];
  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     for (UIView* view in views) {
                       view.frame = CGRectOffset(view.frame, 0, offset);
                     }
                     searchSegmentedControl_.alpha = 1;
                     shelfSeparator_.frame = CGRectOffset(shelfSeparator_.frame, 0, 4);
                     self.tableView.contentOffset = CGPointMake(0, offset);
                   }
                   completion:nil];  
  [self.navigationController setNavigationBarHidden:YES animated:YES];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [super textFieldDidEndEditing:textField];
  CGFloat offset = 44;
  NSArray* views = [NSArray arrayWithObjects:self.searchField, self.cancelButton, self.reloadLabel, self.lastUpdatedLabel, self.arrowImageView, self.spinnerView, nil];
  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     for (UIView* view in views) {
                       view.frame = CGRectOffset(view.frame, 0, offset);
                     }
                     searchSegmentedControl_.alpha = 0;
                     shelfSeparator_.frame = CGRectOffset(shelfSeparator_.frame, 0, -4);
                     self.tableView.contentOffset = CGPointZero;
                   }
                   completion:nil];
  [self.navigationController setNavigationBarHidden:NO animated:YES];
}

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  self.searchResults = nil;
  [self.tableView reloadData];
  return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  NSLog(@"Should search: %d", searchSegmentedControl_.selectedSegmentIndex);
  return YES;
}

#pragma mark - Custom methods.

- (UINavigationController*)navigationController {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  return delegate.navigationController;
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
