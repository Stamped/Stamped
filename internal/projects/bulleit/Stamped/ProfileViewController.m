//
//  ProfileViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "ProfileViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreditsViewController.h"
#import "Entity.h"
#import "RelationshipsViewController.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "STSectionHeaderView.h"
#import "InboxTableViewCell.h"
#import "User.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

static NSString* const kUserStampsPath = @"/collections/user.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";
static NSString* const kFriendshipCheckPath = @"/friendships/check.json";
static NSString* const kFriendshipCreatePath = @"friendships/create.json";
static NSString* const kFriendshipRemovePath = @"friendships/remove.json";

@interface ProfileViewController ()
- (void)loadStampsFromNetwork;
- (void)loadUserInfoFromNetwork;
- (void)fillInUserData;
- (void)loadRelationshipData;

@property (nonatomic, copy) NSArray* stampsArray;
@end

@implementation ProfileViewController

@synthesize userImageView = userImageView_;
@synthesize cameraButton = cameraButton_;
@synthesize creditCountLabel = creditCountLabel_;
@synthesize followerCountLabel = followerCountLabel_;
@synthesize followingCountLabel = followingCountLabel_;
@synthesize fullNameLabel = fullNameLabel_;
@synthesize usernameLocationLabel = usernameLocationLabel_;
@synthesize bioLabel = bioLabel_;
@synthesize shelfImageView = shelfImageView_;
@synthesize toolbarView = toolbarView_;
@synthesize tableView = tableView_;
@synthesize user = user_;
@synthesize stampsArray = stampsArray_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;
@synthesize followIndicator = followIndicator_;

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];  
}

- (void)dealloc {
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.user = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  userImageView_.imageURL = user_.profileImageURL;
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(57, -10, 61, 61);
  stampLayer.opacity = 0.95;
  stampLayer.contents = (id)user_.stampImage.CGImage;
  [shelfImageView_.superview.layer insertSublayer:stampLayer below:shelfImageView_.layer];
  [stampLayer release];
  cameraButton_.hidden = YES;
  //cameraButton_.hidden = ![user_.userID isEqualToString:[AccountManager sharedManager].currentUser.userID];
  fullNameLabel_.textColor = [UIColor stampedBlackColor];
  usernameLocationLabel_.textColor = [UIColor stampedLightGrayColor];
  bioLabel_.font = [UIFont fontWithName:@"Helvetica-Oblique" size:12];
  bioLabel_.textColor = [UIColor stampedGrayColor];
  if (user_.firstName)
    [self fillInUserData];

  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.855 alpha:1.0].CGColor, nil];
  toolbarGradient.frame = toolbarView_.bounds;
  [toolbarView_.layer addSublayer:toolbarGradient];
  [toolbarGradient release];
  
  toolbarView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:toolbarView_.bounds].CGPath;
  toolbarView_.layer.shadowOpacity = 0.2;
  toolbarView_.layer.shadowOffset = CGSizeMake(0, -1);
  toolbarView_.alpha = 0.9;
  [self loadRelationshipData];
  [self loadStampsFromNetwork];
  [self loadUserInfoFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.userImageView = nil;
  self.cameraButton = nil;
  self.creditCountLabel = nil;
  self.followerCountLabel = nil;
  self.followingCountLabel = nil;
  self.fullNameLabel = nil;
  self.usernameLocationLabel = nil;
  self.bioLabel = nil;
  self.shelfImageView = nil;
  self.toolbarView = nil;
  self.tableView = nil;
  self.followIndicator = nil;
  self.followButton = nil;
  self.unfollowButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (IBAction)followButtonPressed:(id)sender {
  followButton_.hidden = YES;
  followIndicator_.hidden = NO;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kFriendshipCreatePath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id", nil];
  [objectLoader send];
}

- (IBAction)unfollowButtonPressed:(id)sender {
  unfollowButton_.hidden = YES;
  followIndicator_.hidden = NO;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kFriendshipRemovePath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id", nil];
  [objectLoader send];
}

- (IBAction)creditsButtonPressed:(id)sender {
  CreditsViewController* creditsViewController =
      [[CreditsViewController alloc] initWithNibName:@"CreditsViewController" bundle:nil];
  [self.navigationController pushViewController:creditsViewController animated:YES];
  [creditsViewController release];
}

- (IBAction)followersButtonPressed:(id)sender {
  RelationshipsViewController* relationshipsViewController =
      [[RelationshipsViewController alloc] initWithRelationship:RelationshipTypeFollowers];
  relationshipsViewController.user = user_;
  [self.navigationController pushViewController:relationshipsViewController animated:YES];
  [relationshipsViewController release];
}

- (IBAction)followingButtonPressed:(id)sender {
  RelationshipsViewController* relationshipsViewController =
      [[RelationshipsViewController alloc] initWithRelationship:RelationshipTypeFriends];
  relationshipsViewController.user = user_;
  [self.navigationController pushViewController:relationshipsViewController animated:YES];
  [relationshipsViewController release];
}

- (IBAction)cameraButtonPressed:(id)sender {
  NSLog(@"Camera...");
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return self.stampsArray.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.stamp = (Stamp*)[stampsArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  view.leftLabel.text = @"Stamps";
  view.rightLabel.text = [user_.numStamps stringValue];
  
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [stampsArray_ objectAtIndex:indexPath.row];
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];

  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath rangeOfString:kUserLookupPath].location != NSNotFound) {
    self.user = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", user_.screenName]];
    [self fillInUserData];
  }

  if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath]) {
    followIndicator_.hidden = YES;
    unfollowButton_.hidden = NO;
    followButton_.hidden = YES;
    user_.numFollowers = [NSNumber numberWithInt:[user_.numFollowers intValue] + 1];
    followerCountLabel_.text = [user_.numFollowers stringValue];
  }

  if ([objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    followIndicator_.hidden = YES;
    unfollowButton_.hidden = YES;
    followButton_.hidden = NO;
    user_.numFollowers = [NSNumber numberWithInt:[user_.numFollowers intValue] - 1];
    followerCountLabel_.text = [user_.numFollowers stringValue];
  }
  
  if ([objectLoader.resourcePath rangeOfString:kUserStampsPath].location != NSNotFound) {
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    self.stampsArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:descriptor]];
    [self.tableView reloadData];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [objectLoader send];
    return;
  }
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if ([request.resourcePath rangeOfString:kFriendshipCheckPath].location != NSNotFound) {
    followIndicator_.hidden = YES;
    if ([response.bodyAsString isEqualToString:@"false"]) {
      followButton_.hidden = NO;
    } else {
      unfollowButton_.hidden = NO;
    }
  }
}

#pragma mark - Private methods.

- (void)loadRelationshipData {
  NSString* currentUserID = [AccountManager sharedManager].currentUser.userID;
  if (!currentUserID)
    return;

  if ([currentUserID isEqualToString:user_.userID]) {
    followIndicator_.hidden = YES;
    toolbarView_.hidden = YES;
    return;
  }
  followIndicator_.hidden = NO;
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kFriendshipCheckPath delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:currentUserID, @"user_id_a",
                                                              user_.userID, @"user_id_b", nil];
  [request send];
}

- (void)fillInUserData {
  fullNameLabel_.text = [NSString stringWithFormat:@"%@ %@", user_.firstName, user_.lastName];
  usernameLocationLabel_.text = [NSString stringWithFormat:@"%@  /  %@", user_.screenName, @"Scranton, PA"];
  bioLabel_.text = user_.bio;
  creditCountLabel_.text = [user_.numCredits stringValue];
  followerCountLabel_.text = [user_.numFollowers stringValue];
  followingCountLabel_.text = [user_.numFriends stringValue];
  [self.tableView reloadData];
}

- (void)loadUserInfoFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* username = user_.screenName;
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath delegate:self];
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithKeysAndObjects:@"screen_names", username, nil];
  [objectLoader send];
}

- (void)loadStampsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserStampsPath
                                                                    delegate:self];
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id", nil];
  [objectLoader send];
}

@end
