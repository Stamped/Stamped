//
//  ProfileViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "ProfileViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreditsViewController.h"
#import "Entity.h"
#import "FriendshipManager.h"
#import "EditProfileViewController.h"
#import "RelationshipsViewController.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "ShowImageViewController.h"
#import "STSectionHeaderView.h"
#import "StampListViewController.h"
#import "InboxTableViewCell.h"
#import "User.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "Util.h"

static NSString* const kUserStampsPath = @"/collections/user.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";
static NSString* const kFriendshipCheckPath = @"/friendships/check.json";
static NSString* const kFriendshipCreatePath = @"/friendships/create.json";
static NSString* const kFriendshipRemovePath = @"/friendships/remove.json";

@interface ProfileViewController ()
- (void)userImageTapped:(id)sender;
- (void)editButtonPressed:(id)sender;
- (void)loadStampsFromNetwork;
- (void)loadStampsFromDataStore;
- (void)loadUserInfoFromNetwork;
- (void)fillInUserData;
- (void)loadRelationshipData;
- (void)addStampsRemainingLayer;
- (void)updateStampsRemainingLayer;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;

@property (nonatomic, readonly) CATextLayer* stampsRemainingLayer;
@property (nonatomic, readonly) CALayer* stampLayer;
@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@end

@implementation ProfileViewController

@synthesize userImageView = userImageView_;
@synthesize creditCountLabel = creditCountLabel_;
@synthesize followerCountLabel = followerCountLabel_;
@synthesize followingCountLabel = followingCountLabel_;
@synthesize fullNameLabel = fullNameLabel_;
@synthesize usernameLocationLabel = usernameLocationLabel_;
@synthesize bioLabel = bioLabel_;
@synthesize toolbarView = toolbarView_;
@synthesize tableView = tableView_;
@synthesize user = user_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;
@synthesize followIndicator = followIndicator_;
@synthesize stampsAreTemporary = stampsAreTemporary_;
@synthesize stampsRemainingLayer = stampsRemainingLayer_;
@synthesize stampLayer = stampLayer_;
@synthesize fetchedResultsController = fetchedResultsController_;

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];  
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.user = nil;
  self.userImageView = nil;
  self.creditCountLabel = nil;
  self.followerCountLabel = nil;
  self.followingCountLabel = nil;
  self.fullNameLabel = nil;
  self.usernameLocationLabel = nil;
  self.bioLabel = nil;
  self.toolbarView = nil;
  self.tableView = nil;
  self.followIndicator = nil;
  self.followButton = nil;
  self.unfollowButton = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  userImageView_.imageURL = user_.profileImageURL;
  userImageView_.enabled = YES;
  [userImageView_ addTarget:self
                     action:@selector(userImageTapped:)
           forControlEvents:UIControlEventTouchUpInside];

  stampLayer_ = [[CALayer alloc] init];
  stampLayer_.frame = CGRectMake(57, -10, 61, 61);
  stampLayer_.opacity = 0.95;
  stampLayer_.contents = (id)user_.stampImage.CGImage;
  [userImageView_.superview.layer insertSublayer:stampLayer_ above:userImageView_.layer];
  [stampLayer_ release];
  fullNameLabel_.textColor = [UIColor stampedBlackColor];
  usernameLocationLabel_.textColor = [UIColor stampedLightGrayColor];
  bioLabel_.font = [UIFont fontWithName:@"Helvetica-Oblique" size:12];
  bioLabel_.textColor = [UIColor stampedGrayColor];
  if (user_.name)
    [self fillInUserData];

  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:user_.screenName
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
  
  if ([user_.screenName isEqualToString:[AccountManager sharedManager].currentUser.screenName]) {
    UIBarButtonItem* editButton = [[UIBarButtonItem alloc] initWithTitle:@"Edit"
                                                                   style:UIBarButtonItemStylePlain
                                                                  target:self
                                                                  action:@selector(editButtonPressed:)];
    [self.navigationItem setRightBarButtonItem:editButton];
    [editButton release];
  }
  
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
  toolbarView_.alpha = 0.85;
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
  [self loadUserInfoFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userImageView = nil;
  self.creditCountLabel = nil;
  self.followerCountLabel = nil;
  self.followingCountLabel = nil;
  self.fullNameLabel = nil;
  self.usernameLocationLabel = nil;
  self.bioLabel = nil;
  self.toolbarView = nil;
  self.tableView = nil;
  self.followIndicator = nil;
  self.followButton = nil;
  self.unfollowButton = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.navigationController setNavigationBarHidden:NO animated:animated];

  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
  if (!user_.name)
    [self loadUserInfoFromNetwork];
  else
    [self fillInUserData];

  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
  if ([sectionInfo numberOfObjects] == 0)
    [self loadStampsFromNetwork];
  if (followButton_.hidden && unfollowButton_.hidden)
    [self loadRelationshipData];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)userImageTapped:(id)sender {
  ShowImageViewController* controller = [[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil];
  controller.imageURL = user_.largeProfileImageURL;
  [self.navigationController pushViewController:controller animated:YES];
  [controller release];
}

- (void)editButtonPressed:(id)sender {
  EditProfileViewController* vc = [[EditProfileViewController alloc] initWithNibName:@"EditProfileViewController"
                                                                              bundle:nil];
  vc.user = user_;
  [self.navigationController presentModalViewController:vc animated:YES];
  [vc release];
}

#pragma mark - IBActions

- (IBAction)followButtonPressed:(id)sender {
  followButton_.hidden = YES;
  [followIndicator_ startAnimating];
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
  [followIndicator_ startAnimating];
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
      [[CreditsViewController alloc] initWithUser:self.user];
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

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
  [self.tableView reloadData];
}

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [fetchedResultsController_ objectAtIndexPath:indexPath];
  if ([cell respondsToSelector:@selector(setStamp:)])
    [(id)cell setStamp:stamp];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  NSUInteger numStamps = [sectionInfo numberOfObjects];
  if (user_.numStamps.unsignedIntValue > 5 && numStamps > 0)
    return numStamps + 1;

  return numStamps;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:indexPath.section];
  NSUInteger numStamps = [sectionInfo numberOfObjects];
  if (numStamps > 0 && indexPath.row == numStamps) {
    UITableViewCell* allStampsCell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                                             reuseIdentifier:nil] autorelease];
    UILabel* bodyLabel = [[UILabel alloc] initWithFrame:CGRectZero];
    bodyLabel.text = [NSString stringWithFormat:@"View all %d stamps...", user_.numStamps.integerValue];
    bodyLabel.highlightedTextColor = [UIColor whiteColor];
    bodyLabel.textColor = [UIColor colorWithRed:0.48 green:0.61 blue:0.8 alpha:1.0];
    bodyLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:14];
    [bodyLabel sizeToFit];
    bodyLabel.frame = CGRectMake(69, 33, CGRectGetWidth(bodyLabel.frame), CGRectGetHeight(bodyLabel.frame));
    [allStampsCell.contentView addSubview:bodyLabel];
    [bodyLabel release];
    UIImage* disclosureArrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    UIImageView* disclosureImageView = [[UIImageView alloc] initWithImage:disclosureArrowImage 
                                                          highlightedImage:[Util whiteMaskedImageUsingImage:disclosureArrowImage]];
                                         
    disclosureImageView.frame = CGRectMake(300, 37,
                                           CGRectGetWidth(disclosureImageView.frame),
                                           CGRectGetHeight(disclosureImageView.frame));
    [allStampsCell.contentView addSubview:disclosureImageView];
    [disclosureImageView release];
    return allStampsCell;
  }

  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (!cell)
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

  [self configureCell:cell atIndexPath:indexPath];

  return cell;
}

#pragma mark - Table view delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  view.leftLabel.text = @"Recent stamps";
  
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:indexPath.section];
  NSUInteger numStamps = [sectionInfo numberOfObjects];
  if (numStamps > 0 && indexPath.row == numStamps) {
    StampListViewController* vc = [[StampListViewController alloc] init];
    vc.user = user_;
    vc.stampsAreTemporary = stampsAreTemporary_;
    [self.navigationController pushViewController:vc animated:YES];
    [vc release];
    return;
  }
  
  Stamp* stamp = [fetchedResultsController_ objectAtIndexPath:indexPath];
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];

  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath isEqualToString:kUserLookupPath]) {
    self.user = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", user_.screenName]];
    [self fillInUserData];
  }

  if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath]) {
    self.stampsAreTemporary = NO;
    [followIndicator_ stopAnimating];
    unfollowButton_.hidden = NO;
    followButton_.hidden = YES;
    user_.numFollowers = [NSNumber numberWithInt:[user_.numFollowers intValue] + 1];
    followerCountLabel_.text = [user_.numFollowers stringValue];

    [[FriendshipManager sharedManager] followUser:user_];
  }

  if ([objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    self.stampsAreTemporary = YES;
    [followIndicator_ stopAnimating];
    unfollowButton_.hidden = YES;
    followButton_.hidden = NO;
    user_.numFollowers = [NSNumber numberWithInt:[user_.numFollowers intValue] - 1];
    followerCountLabel_.text = [user_.numFollowers stringValue];

    [[FriendshipManager sharedManager] unfollowUser:user_];
  }
  
  if ([objectLoader.resourcePath rangeOfString:kUserStampsPath].location != NSNotFound) {
    self.stampsAreTemporary = stampsAreTemporary_;  // Just fire off the setters logic.
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
    User* currentUser = [AccountManager sharedManager].currentUser;
    [followIndicator_ stopAnimating];
    if ([response.bodyAsString isEqualToString:@"false"]) {
      followButton_.hidden = NO;
      [currentUser removeFollowingObject:user_];
      self.stampsAreTemporary = YES;
    } else {
      unfollowButton_.hidden = NO;
      [currentUser addFollowingObject:user_];
      self.stampsAreTemporary = NO;
    }
  }
}

#pragma mark - Private methods.

- (void)addStampsRemainingLayer {
  stampsRemainingLayer_ = [[CATextLayer alloc] init];
  stampsRemainingLayer_.alignmentMode = kCAAlignmentCenter;
  stampsRemainingLayer_.frame = CGRectMake(0, 
                                           CGRectGetMaxY(self.view.frame) - 30,
                                           CGRectGetWidth(self.view.frame),
                                           CGRectGetHeight(self.view.frame));
  stampsRemainingLayer_.fontSize = 12;
  stampsRemainingLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
  stampsRemainingLayer_.contentsScale = [[UIScreen mainScreen] scale];
  stampsRemainingLayer_.shadowColor = [UIColor whiteColor].CGColor;
  stampsRemainingLayer_.shadowOpacity = 1.0;
  stampsRemainingLayer_.shadowOffset = CGSizeMake(0, 1);
  stampsRemainingLayer_.shadowRadius = 0;
  
  [self updateStampsRemainingLayer];
  [self.view.layer addSublayer:stampsRemainingLayer_];
  [stampsRemainingLayer_ release];
}

- (void)updateStampsRemainingLayer {
  if (!stampsRemainingLayer_)
    return;

  NSString* stampsLeft = [[AccountManager sharedManager].currentUser.numStampsLeft stringValue];
  if (!stampsLeft)
    return;

  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* full = [NSString stringWithFormat:@"You have %@ stamps remaining", stampsLeft];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName
                 value:(id)font 
                 range:[full rangeOfString:stampsLeft]];
  CFRelease(font);
  CFRelease(style);
  stampsRemainingLayer_.string = string;
  [string release];
}

- (void)loadRelationshipData {
  NSString* currentUserID = [AccountManager sharedManager].currentUser.userID;
  if (!currentUserID)
    return;

  if ([currentUserID isEqualToString:user_.userID]) {
    [followIndicator_ stopAnimating];
    followButton_.hidden = YES;
    unfollowButton_.hidden = YES;
    [self addStampsRemainingLayer];
    return;
  }
  [followIndicator_ startAnimating];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kFriendshipCheckPath delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:currentUserID, @"user_id_a",
                                                              user_.userID, @"user_id_b", nil];
  [request send];
}

- (void)fillInUserData {
  fullNameLabel_.text = user_.name;
  if (!user_.location)
    usernameLocationLabel_.text = user_.screenName;
  else
    usernameLocationLabel_.text = [NSString stringWithFormat:@"%@ / %@", user_.screenName, user_.location];

  bioLabel_.text = user_.bio;
  creditCountLabel_.text = [user_.numCredits stringValue];
  followerCountLabel_.text = [user_.numFollowers stringValue];
  followingCountLabel_.text = [user_.numFriends stringValue];
  stampLayer_.contents = (id)user_.stampImage.CGImage;
  [self updateStampsRemainingLayer];
}

- (void)loadUserInfoFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* username = user_.screenName;
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithKeysAndObjects:@"screen_names", username, nil];
  [objectLoader send];
}

- (void)loadStampsFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserStampsPath
                                                                    delegate:self];
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id",
                                                                   @"1", @"quality",
                                                                   @"5", @"limit", nil];
  [objectLoader send];
}

- (void)loadStampsFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Stamp fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    [request setPredicate:[NSPredicate predicateWithFormat:@"deleted == NO AND user.userID == %@", user_.userID]];
    [request setFetchLimit:5];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Stamp managedObjectContext]
                                              sectionNameKeyPath:nil
                                                       cacheName:nil];
    self.fetchedResultsController = fetchedResultsController;
    fetchedResultsController.delegate = self;
    [fetchedResultsController release];
  }
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
}

@end
