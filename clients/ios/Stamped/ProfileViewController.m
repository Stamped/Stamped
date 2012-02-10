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

#import "AccountManager.h"
#import "CreditsViewController.h"
#import "Entity.h"
#import "FriendshipManager.h"
#import "EditProfileViewController.h"
#import "PeopleListViewController.h"
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
#import "Alerts.h"

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
- (void)updateStampCounterLayer;
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)showEarnMoreModal;
- (void)earnMoreModalTapped:(UIGestureRecognizer*)recognizer;
- (void)stampCountWasTapped:(UIGestureRecognizer*)recognizer;

@property (nonatomic, readonly) CATextLayer* stampCounterLayer;
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
@synthesize stampCounterLayer = stampCounterLayer_;
@synthesize stampLayer = stampLayer_;
@synthesize fetchedResultsController = fetchedResultsController_;
@synthesize screenName = screenName_;

- (id)init {
  self = [super initWithNibName:@"ProfileViewController" bundle:nil];
  if (self) {}
  return self;
}

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
  self.screenName = nil;
  stampLayer_ = nil;
  stampCounterLayer_ = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  userImageView_.imageURL = [user_ profileImageURLForSize:ProfileImageSize72];
  userImageView_.enabled = YES;
  [userImageView_ addTarget:self
                     action:@selector(userImageTapped:)
           forControlEvents:UIControlEventTouchUpInside];

  stampLayer_ = [[CALayer alloc] init];
  stampLayer_.frame = CGRectMake(58, -10, 60, 60);
  stampLayer_.opacity = 0.95;
  stampLayer_.contents = (id)[user_ stampImageWithSize:StampImageSize60].CGImage;
  [userImageView_.superview.layer insertSublayer:stampLayer_ above:userImageView_.layer];
  [stampLayer_ release];
  fullNameLabel_.textColor = [UIColor stampedBlackColor];
  usernameLocationLabel_.textColor = [UIColor stampedLightGrayColor];
  bioLabel_.font = [UIFont fontWithName:@"Helvetica-Oblique" size:12];
  bioLabel_.textColor = [UIColor stampedGrayColor];

  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:user_.screenName]
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
  
  User* currentUser = [AccountManager sharedManager].currentUser;
  if ([user_.screenName isEqualToString:currentUser.screenName]) {
    UIBarButtonItem* editButton = [[UIBarButtonItem alloc] initWithTitle:@"Edit"
                                                                   style:UIBarButtonItemStylePlain
                                                                  target:self
                                                                  action:@selector(editButtonPressed:)];
    [self.navigationItem setRightBarButtonItem:editButton];
    [editButton release];
    [self addStampsRemainingLayer];
  } else {
    if ([currentUser.following containsObject:user_]) {
      unfollowButton_.hidden = NO;
      self.stampsAreTemporary = NO;
    } else {
      followButton_.hidden = NO;
      self.stampsAreTemporary = YES;
    }
  }

  if (user_.name)
    [self fillInUserData];

  self.highlightView.backgroundColor = [UIColor whiteColor];
  CAGradientLayer* highlightGradientLayer = [[CAGradientLayer alloc] init];
  highlightGradientLayer.frame = CGRectMake(0, 0, 320, 20);
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:user_.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (user_.secondaryColor) {
    [Util splitHexString:user_.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  highlightGradientLayer.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:1.0].CGColor,
           (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:1.0].CGColor, nil];
  
  highlightGradientLayer.startPoint = CGPointMake(0.0, 0.5);
  highlightGradientLayer.endPoint = CGPointMake(1.0, 0.5);
  [self.highlightView.layer addSublayer:highlightGradientLayer];
  [highlightGradientLayer release];
  self.highlightView.alpha = 1.0;
  
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
  [self loadUserInfoFromNetwork];
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
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
  stampLayer_ = nil;
  stampCounterLayer_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.navigationController setNavigationBarHidden:NO animated:animated];

  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
  if (!user_.name && RKClient.sharedClient.requestQueue.count == 0)
    [self loadUserInfoFromNetwork];
  else
    [self fillInUserData];
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
  PeopleListViewController* vc =
      [[PeopleListViewController alloc] initWithSource:PeopleListSourceTypeFollowers];
  vc.user = user_;
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (IBAction)followingButtonPressed:(id)sender {
  PeopleListViewController* vc =
      [[PeopleListViewController alloc] initWithSource:PeopleListSourceTypeFriends];
  vc.user = user_;
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
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
    UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"All Stamps"
                                                                   style:UIBarButtonItemStyleBordered
                                                                  target:nil
                                                                  action:nil];
    [[vc navigationItem] setBackBarButtonItem:backButton];
    [backButton release];
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
    id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:0];
    if (user_.numStamps.unsignedIntValue > 0 && [sectionInfo numberOfObjects] == 0)
      [self loadStampsFromNetwork];
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
  if (!response.isOK) {
    if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound) {
      [followIndicator_ stopAnimating];
      followButton_.hidden = NO;
      // Error catching.
      switch (response.statusCode) {
          break;
        case 400:
        case 500: {
          [[Alerts alertWithTemplate:AlertTemplateDefault] show];
          break;
        }
        case 200: {
          UIAlertView* alertView = [[UIAlertView alloc] initWithTitle:@"Already Following"
                                                              message:@""
                                                             delegate:nil
                                                    cancelButtonTitle:@"Fair Enough"
                                                    otherButtonTitles:nil];
          NSError* err = nil;
          NSString* username = nil;
          id body = [response parsedBody:&err];
          if (!err) {
            username = [body objectForKey:@"username"];
          }
          alertView.title = @"Already Following";
          if (username)
            alertView.message = [NSString stringWithFormat: @"You're already following %@.", username];
          else 
            alertView.message = @"You're already following that person.";
          [alertView show];
          [alertView release];
          break;
        }
        default:
          break;
      }
      return;
    }
    if ([request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound) {
      [followIndicator_ stopAnimating];
      unfollowButton_.hidden = NO;
      [[Alerts alertWithTemplate:AlertTemplateDefault] show];
      return;
    }
  }
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

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound) {
    followButton_.hidden = NO;
  }
  else if ([request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound) {
    unfollowButton_.hidden = NO;
  }
  RKClient* client = [RKClient sharedClient];
  
  if (error.code == 2) {
    if (followIndicator_.isAnimating)
      [[Alerts alertWithTemplate:AlertTemplateNoInternet] show];
  } else if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable) {
    [[Alerts alertWithTemplate:AlertTemplateDefault] show];
  }
  [followIndicator_ stopAnimating];
  NSLog(@"Error %@ for request %@", error, request.resourcePath);
}

- (void)requestDidTimeout:(RKRequest *)request {
  if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound) {
    [followIndicator_ stopAnimating];
    followButton_.hidden = NO;
  }
  else if ([request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound) {
    [followIndicator_ stopAnimating];
    unfollowButton_.hidden = NO;
  }
  [[Alerts alertWithTemplate:AlertTemplateTimedOut] show];
  NSLog(@"Request %@ timed out", request.resourcePath);
}

#pragma mark - Private methods.

- (void)showEarnMoreModal {
  UIView* overlayContainer = [[UIView alloc] initWithFrame:self.view.window.frame];
  overlayContainer.backgroundColor = [UIColor clearColor];
  overlayContainer.alpha = 0;
  UIView* black = [[UIView alloc] initWithFrame:overlayContainer.bounds];
  black.backgroundColor = [UIColor blackColor];
  black.alpha = 0.75;
  [overlayContainer addSubview:black];
  [black release];
  UIImageView* earnMore = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"earn_tip_profile"]];
  earnMore.center = overlayContainer.center;
  [overlayContainer addSubview:earnMore];
  [earnMore release];
  User* currentUser = [AccountManager sharedManager].currentUser;
  UIImageView* creditLeft = [[UIImageView alloc] initWithImage:[Util gradientImage:[UIImage imageNamed:@"stamp_28pt_texture"]
                                                                  withPrimaryColor:currentUser.primaryColor
                                                                         secondary:currentUser.secondaryColor]];
  creditLeft.frame = CGRectOffset(creditLeft.frame, 62, 75);
  [earnMore addSubview:creditLeft];
  [creditLeft release];
  UIImageView* creditRight = [[UIImageView alloc] initWithImage:[Util gradientImage:[UIImage imageNamed:@"stamp_28pt_solid"]
                                                                   withPrimaryColor:currentUser.primaryColor
                                                                          secondary:currentUser.secondaryColor]];
  creditRight.frame = CGRectOffset(creditLeft.frame, 14, 0);
  [earnMore addSubview:creditRight];
  [creditRight release];
  UIImageView* creditOverlay = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_28pt_overlaySolid"]];
  creditOverlay.center = creditRight.center;
  [earnMore addSubview:creditOverlay];
  [creditOverlay release];
  UITapGestureRecognizer* recognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(earnMoreModalTapped:)];
  [overlayContainer addGestureRecognizer:recognizer];
  [recognizer release];
  [self.view.window addSubview:overlayContainer];
  [UIView animateWithDuration:0.3 animations:^{
    overlayContainer.alpha = 1;
  }];
  [overlayContainer release];
}

- (void)earnMoreModalTapped:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;
  
  [UIView animateWithDuration:0.3 animations:^{
    recognizer.view.alpha = 0.0;
  } completion:^(BOOL finished) {
    [recognizer.view removeFromSuperview];
  }];
}

- (void)stampCountWasTapped:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [self showEarnMoreModal];
}

- (void)addStampsRemainingLayer {
  CATextLayer* stampsRemainingLayer = [[CATextLayer alloc] init];
  stampsRemainingLayer.alignmentMode = kCAAlignmentCenter;
  stampsRemainingLayer.frame = CGRectMake(0, 
                                          CGRectGetMaxY(self.view.frame) - 30,
                                          CGRectGetWidth(self.view.frame),
                                          CGRectGetHeight(self.view.frame));
  stampsRemainingLayer.fontSize = 12;
  stampsRemainingLayer.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
  stampsRemainingLayer.contentsScale = [[UIScreen mainScreen] scale];
  stampsRemainingLayer.shadowColor = [UIColor whiteColor].CGColor;
  stampsRemainingLayer.shadowOpacity = 1.0;
  stampsRemainingLayer.shadowOffset = CGSizeMake(0, 1);
  stampsRemainingLayer.shadowRadius = 0;
  stampsRemainingLayer.string = @"You have            stamps remaining";

  [self.view.layer addSublayer:stampsRemainingLayer];
  [stampsRemainingLayer release];
  UIImage* coloredImage = [Util gradientImage:[UIImage imageNamed:@"stampcount_color"]
                             withPrimaryColor:user_.primaryColor
                                    secondary:user_.secondaryColor];
  UIImageView* colorView = [[UIImageView alloc] initWithImage:coloredImage];
  colorView.frame = CGRectMake(121, CGRectGetMaxY(self.view.frame) - 41,
                               CGRectGetWidth(colorView.frame), CGRectGetHeight(colorView.frame));
  [self.view addSubview:colorView];
  [colorView release];
  UIImageView* textureView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stampcount_texture"]];
  textureView.center = colorView.center;
  textureView.userInteractionEnabled = YES;
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(stampCountWasTapped:)];
  [textureView addGestureRecognizer:recognizer];
  [recognizer release];
  [self.view addSubview:textureView];
  [textureView release];
  stampCounterLayer_ = [[CATextLayer alloc] init];
  stampCounterLayer_.fontSize = 20;
  stampCounterLayer_.foregroundColor = [UIColor colorWithWhite:0.9 alpha:1].CGColor;
  stampCounterLayer_.contentsScale = [[UIScreen mainScreen] scale];
  stampCounterLayer_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.6].CGColor;
  stampCounterLayer_.shadowOpacity = 1.0;
  stampCounterLayer_.shadowOffset = CGSizeMake(0, 2);
  stampCounterLayer_.shadowRadius = 2;
  stampCounterLayer_.alignmentMode = kCAAlignmentCenter;
  CGFontRef font = CGFontCreateWithFontName((CFStringRef)@"TitlingGothicFB-StandardSkyline");
  stampCounterLayer_.font = font;
  stampCounterLayer_.frame = CGRectOffset(textureView.frame, 0, 5);
  CFRelease(font);
  [self.view.layer addSublayer:stampCounterLayer_];
  [stampCounterLayer_ release];
  [self updateStampCounterLayer];
}

- (void)updateStampCounterLayer {
  NSNumber* numStamps = [AccountManager sharedManager].currentUser.numStampsLeft;
  NSString* stampsLeft = numStamps.stringValue;
  if (numStamps.integerValue > 999)
    stampsLeft = @"999+";

  if (!stampsLeft)
    return;
  
  stampCounterLayer_.string = stampsLeft;
}

- (void)loadRelationshipData {
  NSString* currentUserID = [AccountManager sharedManager].currentUser.userID;
  if (!currentUserID || [currentUserID isEqualToString:user_.userID])
    return;

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
  stampLayer_.contents = (id)[user_ stampImageWithSize:StampImageSize60].CGImage;
  [self updateStampCounterLayer];
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

#pragma mark - UIScrollViewDelegate Methods.

- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
  [super scrollViewDidScroll:scrollView];
  self.highlightView.alpha = MIN(1.0, (15 + (-self.shelfView.frame.origin.y - 356)) / 15);
}

@end
