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
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "STSectionHeaderView.h"
#import "InboxTableViewCell.h"
#import "User.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

static NSString* const kUserStampsPath = @"/collections/user.json";

@interface ProfileViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;

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

@synthesize user = user_;
@synthesize stampsArray = stampsArray_;

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
  fullNameLabel_.text = [NSString stringWithFormat:@"%@ %@", user_.firstName, user_.lastName];
  usernameLocationLabel_.textColor = [UIColor stampedLightGrayColor];
  usernameLocationLabel_.text = [NSString stringWithFormat:@"%@  /  %@", user_.screenName, @"Scranton, PA"];
  bioLabel_.font = [UIFont fontWithName:@"Helvetica-Oblique" size:12];
  bioLabel_.textColor = [UIColor stampedGrayColor];
  bioLabel_.text = user_.bio;
  creditCountLabel_.text = [user_.numCredits stringValue];
  followerCountLabel_.text = [user_.numFollowers stringValue];
  followingCountLabel_.text = [user_.numFriends stringValue];
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
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

- (IBAction)creditsButtonPressed:(id)sender {
  CreditsViewController* creditsViewController =
      [[CreditsViewController alloc] initWithNibName:@"CreditsViewController" bundle:nil];
  [self.navigationController pushViewController:creditsViewController animated:YES];
  [creditsViewController release];
}

- (IBAction)followersButtonPressed:(id)sender {
  NSLog(@"Followers...");
}

- (IBAction)followingButtonPressed:(id)sender {
  NSLog(@"Following...");
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
  STSectionHeaderView* view = [[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)];
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

#pragma mark - STReloadableViewController Methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadStampsFromNetwork];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[self loadStampsFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadStampsFromNetwork];
    return;
  }
  
  [self setIsLoading:NO];
}

#pragma mark - Private methods.

- (void)loadStampsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  NSString* authToken = [AccountManager sharedManager].authToken.accessToken;
  NSString* resourcePath = [kUserStampsPath appendQueryParams:[NSDictionary dictionaryWithObjectsAndKeys:authToken, @"oauth_token", user_.userID, @"user_id", nil]];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:stampMapping
                                  delegate:self];
}

- (void)loadStampsFromDataStore {
  self.stampsArray = nil;
  NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  [request setPredicate:[NSPredicate predicateWithFormat:@"user.screenName == %@", user_.screenName]];
	self.stampsArray = [Stamp objectsWithFetchRequest:request];
  [self.tableView reloadData];
}

@end
