//
//  StampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "Comment.h"
#import "Entity.h"
#import "Favorite.h"
#import "Notifications.h"
#import "ProfileViewController.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "STImageView.h"
#import "StampDetailCommentView.h"
#import "ShowImageViewController.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

static const CGFloat kMainCommentFrameMinHeight = 75.0;
static const CGFloat kKeyboardHeight = 216.0;
static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static NSString* const kCreateLikePath = @"/stamps/likes/create.json";
static NSString* const kRemoveLikePath = @"/stamps/likes/remove.json";
static NSString* const kCreateCommentPath = @"/comments/create.json";
static NSString* const kCommentsPath = @"/comments/show.json";

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbar;
- (void)setUpMainContentView;
- (void)setUpCommentsView;
- (void)addUserGradientBackground;
- (void)addCreditedUser:(User*)creditedUser;
- (NSAttributedString*)creditAttributedString:(User*)creditedUser;
- (void)setNumLikes:(NSUInteger)likes;
- (void)setMainCommentContainerFrame:(CGRect)mainCommentFrame;
- (void)handleTap:(UITapGestureRecognizer*)recognizer;
- (void)handlePhotoTap:(UITapGestureRecognizer*)recognizer;
- (void)handleEntityTap:(UITapGestureRecognizer*)recognizer;
- (void)handleCommentUserImageViewTap:(NSNotification*)notification;
- (void)handleUserImageViewTap:(id)sender;
- (void)renderComments;
- (void)addComment:(Comment*)comment;
- (void)loadCommentsFromServer;
- (void)preloadEntityView;

@property (nonatomic, readonly) STImageView* stampPhotoView;
@property (nonatomic, readonly) UIImageView* likeFaceImageView;
@property (nonatomic, readonly) UILabel* numLikesLabel;
@property (nonatomic, assign) NSUInteger numLikes;
@end

@implementation StampDetailViewController

@synthesize headerView = headerView_;
@synthesize mainCommentContainer = mainCommentContainer_;
@synthesize scrollView = scrollView_;
@synthesize addCommentField = addCommentField_;
@synthesize commentsView = commentsView_;
@synthesize activityView = activityView_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize currentUserImageView = currentUserImageView_;
@synthesize commenterImageView = commenterImageView_;
@synthesize commenterNameLabel = commenterNameLabel_;
@synthesize stampedLabel = stampedLabel_;
@synthesize loadingView = loadingView_;
@synthesize addFavoriteButton = addFavoriteButton_;
@synthesize addFavoriteLabel = addFavoriteLabel_;
@synthesize likeButton = likeButton_;
@synthesize likeLabel = likeLabel_;
@synthesize shareLabel = shareLabel_;
@synthesize shareButton = shareButton_;
@synthesize stampLabel = stampLabel_;
@synthesize stampButton = stampButton_;
@synthesize stampPhotoView = stampPhotoView_;
@synthesize eDetailArrowImageView = eDetailArrowImageView_;
@synthesize likeFaceImageView = likeFaceImageView_;
@synthesize numLikesLabel = numLikesLabel_;
@synthesize numLikes = numLikes_;

- (id)initWithStamp:(Stamp*)stamp {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    stamp_ = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [stamp_ release];
  [detailViewController_ release];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.headerView = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.loadingView = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteLabel = nil;
  self.likeButton = nil;
  self.likeLabel = nil;
  self.shareLabel = nil;
  self.shareButton = nil;
  self.stampLabel = nil;
  self.stampButton = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [super viewWillDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(handleCommentUserImageViewTap:)
                                               name:kCommentUserImageTappedNotification
                                             object:nil];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self preloadEntityView];
  stampPhotoView_.imageURL = stamp_.imageURL;
  [super viewDidAppear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];

  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
  [self.view addGestureRecognizer:gestureRecognizer];
  gestureRecognizer.cancelsTouchesInView = NO;
  [gestureRecognizer release];

  scrollView_.contentSize = self.view.bounds.size;

  [self setUpToolbar];
  [self setUpHeader];

  activityView_.layer.shadowOpacity = 0.1;
  activityView_.layer.shadowOffset = CGSizeMake(0, 1);
  activityView_.layer.shadowRadius = 2;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  mainCommentContainer_.layer.shadowOpacity = 0.1;
  mainCommentContainer_.layer.shadowOffset = CGSizeMake(0, 0);
  mainCommentContainer_.layer.shadowRadius = 2;
  mainCommentContainer_.layer.shadowPath =
      [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;
  
  [self setUpMainContentView];
  [self setUpCommentsView];

  [self renderComments];
  [self loadCommentsFromServer];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.headerView = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.loadingView = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteLabel = nil;
  self.likeButton = nil;
  self.likeLabel = nil;
  self.shareLabel = nil;
  self.shareButton = nil;
  self.stampLabel = nil;
  self.stampButton = nil;
}

- (void)setUpHeader {
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  CGSize stringSize = [stamp_.entityObject.title sizeWithFont:[UIFont fontWithName:fontString size:fontSize]
                                                     forWidth:250
                                                lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(15, 15, stringSize.width, stringSize.height)];
  nameLabel.font = [UIFont fontWithName:fontString size:fontSize];
  nameLabel.text = stamp_.entityObject.title;
  nameLabel.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  nameLabel.backgroundColor = [UIColor clearColor];
  [headerView_ addSubview:nameLabel];
  [nameLabel release];

  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                17 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)stamp_.user.stampImage.CGImage;
  [headerView_.layer addSublayer:stampLayer];
  [stampLayer release];
  
  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)stamp_.entityObject.categoryImage.CGImage;
  typeIconLayer.frame = CGRectMake(17, 50, 15, 12);
  [headerView_.layer addSublayer:typeIconLayer];
  [typeIconLayer release];
  
  UILabel* detailLabel =
      [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeIconLayer.frame) + 4, 49, 258, 15)];
  detailLabel.opaque = NO;
  detailLabel.backgroundColor = [UIColor clearColor];
  detailLabel.text = stamp_.entityObject.subtitle;
  detailLabel.font = [UIFont fontWithName:@"Helvetica" size:11];
  detailLabel.textColor = [UIColor stampedGrayColor];
  [headerView_ addSubview:detailLabel];
  [detailLabel release];

  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self 
                                              action:@selector(handleEntityTap:)];
  [headerView_ addGestureRecognizer:gestureRecognizer];
  [gestureRecognizer release];
}

- (void)setUpToolbar {
  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.855 alpha:1.0].CGColor, nil];
  toolbarGradient.frame = bottomToolbar_.bounds;
  [bottomToolbar_.layer addSublayer:toolbarGradient];
  [toolbarGradient release];

  bottomToolbar_.layer.shadowPath = [UIBezierPath bezierPathWithRect:bottomToolbar_.bounds].CGPath;
  bottomToolbar_.layer.shadowOpacity = 0.2;
  bottomToolbar_.layer.shadowOffset = CGSizeMake(0, -1);
  bottomToolbar_.alpha = 0.9;
  
  if (stamp_.isFavorited.boolValue) {
    addFavoriteLabel_.text = @"To-Do'd";
    addFavoriteButton_.selected = YES;
  }

  if (stamp_.isLiked.boolValue && stamp_.numLikes.unsignedIntValue > 0) {
    likeLabel_.text = @"Liked";
    likeButton_.selected = YES;
  }
  
  if ([AccountManager sharedManager].currentUser == stamp_.user) {
    stampLabel_.hidden = YES;
    stampButton_.hidden = YES;
    likeLabel_.hidden = YES;
    likeButton_.hidden = YES;
    NSInteger xOffset = 320 / 3;
    // Rearrange To-do and Share buttons to center them.
    CGPoint center = addFavoriteButton_.center;
    center.x = xOffset;
    addFavoriteButton_.center = center;
    center = addFavoriteLabel_.center;
    center.x = xOffset;
    addFavoriteLabel_.center = center;
    xOffset *= 2;
    center = shareLabel_.center;
    center.x = xOffset;
    shareLabel_.center = center;
    center = shareButton_.center;
    center.x = xOffset;
    shareButton_.center = center;
  }
}

- (void)setMainCommentContainerFrame:(CGRect)mainCommentFrame {
  mainCommentContainer_.frame = mainCommentFrame;
  mainCommentContainer_.layer.shadowPath = [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;
  CGRect activityFrame = activityView_.frame;
  activityFrame.size.height = CGRectGetMaxY(mainCommentContainer_.frame) + CGRectGetHeight(commentsView_.bounds) + 5;
  activityView_.frame = activityFrame;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityFrame) + kKeyboardHeight);
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  activityGradientLayer_.frame = activityView_.bounds;
  [CATransaction commit];
}

- (void)setNumLikes:(NSUInteger)likes {
  BOOL adding = numLikes_ < likes;

  numLikes_ = likes;

  numLikesLabel_.hidden = likes == 0;
  likeFaceImageView_.hidden = likes == 0;
  numLikesLabel_.text = [NSNumber numberWithUnsignedInteger:likes].stringValue;
  [numLikesLabel_ sizeToFit];

  // If there is a credited user or an existing like then we already have the room.
  if (stamp_.credits.count > 0 || (adding && numLikes_ > 1) || (!adding && numLikes_ > 0))
    return;

  CGFloat heightDelta = 21;
  if (likes == 0)
    heightDelta *= -1;

  CGRect mainCommentFrame = mainCommentContainer_.frame;
  mainCommentFrame.size.height += heightDelta;
  [self setMainCommentContainerFrame:mainCommentFrame];
  numLikesLabel_.frame = CGRectMake(CGRectGetMaxX(mainCommentFrame) - CGRectGetWidth(numLikesLabel_.frame) - 10,
                                    CGRectGetMaxY(mainCommentFrame) - 30,
                                    CGRectGetWidth(numLikesLabel_.frame),
                                    CGRectGetHeight(numLikesLabel_.frame));
  likeFaceImageView_.frame = CGRectMake(CGRectGetMinX(numLikesLabel_.frame) - CGRectGetWidth(likeFaceImageView_.frame) - 2,
                                        CGRectGetMinY(numLikesLabel_.frame) + 1,
                                        CGRectGetWidth(likeFaceImageView_.frame),
                                        CGRectGetHeight(likeFaceImageView_.frame));
}

- (void)setUpMainContentView {
  commenterImageView_.imageURL = stamp_.user.profileImageURL;
  commenterImageView_.enabled = YES;
  [commenterImageView_ addTarget:self 
                          action:@selector(handleUserImageViewTap:)
                forControlEvents:UIControlEventTouchUpInside];

  commenterNameLabel_.textColor = [UIColor stampedGrayColor];
  commenterNameLabel_.text = stamp_.user.screenName;
  [commenterNameLabel_ sizeToFit];

  [stampedLabel_ sizeToFit];
  CGRect stampedFrame = stampedLabel_.frame;
  stampedFrame.origin.x = CGRectGetMaxX(commenterNameLabel_.frame) + 3;
  stampedLabel_.frame = stampedFrame;
  stampedLabel_.textColor = [UIColor stampedGrayColor];

  UILabel* timestampLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  timestampLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
  timestampLabel.textColor = [UIColor stampedLightGrayColor];
  timestampLabel.textAlignment = UITextAlignmentRight;
  timestampLabel.text = [Util shortUserReadableTimeSinceDate:stamp_.created];
  [timestampLabel sizeToFit];
  timestampLabel.frame = CGRectMake(310 - CGRectGetWidth(timestampLabel.frame) - 10,
                                    10,
                                    CGRectGetWidth(timestampLabel.frame),
                                    CGRectGetHeight(timestampLabel.frame));
  [mainCommentContainer_ addSubview:timestampLabel];
  [timestampLabel release];
  
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  UIFont* commentFont = [UIFont fontWithName:@"Helvetica" size:14];
  commentLabel.font = commentFont;
  commentLabel.textColor = [UIColor colorWithWhite:0.2 alpha:1.0];
  commentLabel.text = stamp_.blurb;
  commentLabel.numberOfLines = 0;
  CGSize stringSize = [stamp_.blurb sizeWithFont:commentFont
                               constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                   lineBreakMode:commentLabel.lineBreakMode];

  const CGFloat leftPadding = CGRectGetMaxX(commenterImageView_.frame) + 10;

  commentLabel.frame = CGRectMake(leftPadding, 25, stringSize.width, stringSize.height);
  [mainCommentContainer_ addSubview:commentLabel];
  [commentLabel release];
  
  CGRect mainCommentFrame = mainCommentContainer_.frame;
  mainCommentFrame.size.height = fmaxf(kMainCommentFrameMinHeight, CGRectGetMaxY(commentLabel.frame) + 10);
  
  if (stamp_.imageURL) {
    stampPhotoView_ = [[STImageView alloc] initWithFrame:CGRectZero];
    NSArray* coordinates = [stamp_.imageDimensions componentsSeparatedByString:@","]; 
    CGFloat width = [(NSString*)[coordinates objectAtIndex:0] floatValue];
    CGFloat height = [(NSString*)[coordinates objectAtIndex:1] floatValue];
    
    stampPhotoView_.frame = CGRectMake(leftPadding,
                                      CGRectGetMaxY(commentLabel.frame) + 8,
                                      200, 200 * (height / width));

    mainCommentFrame.size.height += CGRectGetHeight(stampPhotoView_.bounds) + 10;
    UITapGestureRecognizer* recognizer =
        [[UITapGestureRecognizer alloc] initWithTarget:self
                                                action:@selector(handlePhotoTap:)];
    stampPhotoView_.userInteractionEnabled = YES;
    [stampPhotoView_ addGestureRecognizer:recognizer];
    [recognizer release];
    [mainCommentContainer_ addSubview:stampPhotoView_];
    [stampPhotoView_ release];
  }

  User* creditedUser = [stamp_.credits anyObject];
  if (creditedUser)
    mainCommentFrame.size.height += 33;

  numLikesLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  numLikesLabel_.text = [stamp_.numLikes stringValue];
  numLikes_ = stamp_.numLikes.unsignedIntValue;
  numLikesLabel_.textAlignment = UITextAlignmentRight;
  numLikesLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  numLikesLabel_.textColor = [UIColor stampedGrayColor];
  [mainCommentContainer_ addSubview:numLikesLabel_];
  [numLikesLabel_ release];
  [numLikesLabel_ sizeToFit];

  NSUInteger numLikes = stamp_.numLikes.unsignedIntegerValue;
  if (numLikes > 0 && !creditedUser)
    mainCommentFrame.size.height += 21;

  numLikesLabel_.frame = CGRectMake(CGRectGetMaxX(mainCommentFrame) - CGRectGetWidth(numLikesLabel_.frame) - 10,
                                    CGRectGetMaxY(mainCommentFrame) - 30,
                                    CGRectGetWidth(numLikesLabel_.frame),
                                    CGRectGetHeight(numLikesLabel_.frame));
  likeFaceImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"small_like_icon"]];
  likeFaceImageView_.frame = CGRectMake(CGRectGetMinX(numLikesLabel_.frame) - CGRectGetWidth(likeFaceImageView_.frame) - 2,
                                        CGRectGetMinY(numLikesLabel_.frame) + 1,
                                        CGRectGetWidth(likeFaceImageView_.frame),
                                        CGRectGetHeight(likeFaceImageView_.frame));
  [mainCommentContainer_ addSubview:likeFaceImageView_];
  [likeFaceImageView_ release];

  numLikesLabel_.hidden = (numLikes == 0);
  likeFaceImageView_.hidden = (numLikes == 0);

  [self addUserGradientBackground];
  [self setMainCommentContainerFrame:mainCommentFrame];
  [self addCreditedUser:creditedUser];
}

- (void)addUserGradientBackground {
  activityGradientLayer_ = [[CAGradientLayer alloc] init];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:stamp_.user.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (stamp_.user.secondaryColor) {
    [Util splitHexString:stamp_.user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  activityGradientLayer_.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.9].CGColor,
                                (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.9].CGColor,
                                nil];
  
  activityGradientLayer_.startPoint = CGPointMake(0.0, 0.0);
  activityGradientLayer_.endPoint = CGPointMake(1.0, 1.0);
  [activityView_.layer insertSublayer:activityGradientLayer_ atIndex:0];
  [activityGradientLayer_ release];
}

- (void)addCreditedUser:(User*)creditedUser {
  if (!creditedUser)
    return;

  CALayer* firstStampLayer = [[CALayer alloc] init];
  firstStampLayer.contents = (id)creditedUser.stampImage.CGImage;
  firstStampLayer.frame = CGRectMake(10, CGRectGetMaxY(mainCommentContainer_.frame) - 29, 12, 12);
  [mainCommentContainer_.layer addSublayer:firstStampLayer];
  [firstStampLayer release];
  
  CALayer* secondStampLayer = [[CALayer alloc] init];
  secondStampLayer.contents = (id)stamp_.user.stampImage.CGImage;
  secondStampLayer.frame = CGRectOffset(firstStampLayer.frame, CGRectGetWidth(firstStampLayer.frame) / 2, 0);
  [mainCommentContainer_.layer addSublayer:secondStampLayer];
  [secondStampLayer release];
  
  CATextLayer* creditStringLayer = [[CATextLayer alloc] init];
  creditStringLayer.frame = CGRectMake(CGRectGetMaxX(secondStampLayer.frame) + 5,
                                       CGRectGetMinY(secondStampLayer.frame) + 1, 200, 14);
  creditStringLayer.truncationMode = kCATruncationEnd;
  creditStringLayer.contentsScale = [[UIScreen mainScreen] scale];
  creditStringLayer.fontSize = 12.0;
  creditStringLayer.foregroundColor = [UIColor stampedGrayColor].CGColor;
  creditStringLayer.string = [self creditAttributedString:creditedUser];
  [mainCommentContainer_.layer addSublayer:creditStringLayer];
  [creditStringLayer release];
}

- (NSAttributedString*)creditAttributedString:(User*)creditedUser {
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* user = creditedUser.screenName;
  NSString* full = [NSString stringWithFormat:@"%@ %@", @"Credit to", user];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)[UIColor stampedGrayColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName
                 value:(id)font 
                 range:[full rangeOfString:user options:NSBackwardsSearch]];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}

- (void)setUpCommentsView {
  currentUserImageView_.imageURL = [AccountManager sharedManager].currentUser.profileImageURL;
}

#pragma mark - Toolbar Actions

- (IBAction)handleRestampButtonTap:(id)sender {
  CreateStampViewController* createViewController =
      [[CreateStampViewController alloc] initWithEntityObject:stamp_.entityObject
                                                   creditedTo:stamp_.user];
  [self.navigationController pushViewController:createViewController animated:YES];
  [createViewController release];
}

- (IBAction)handleTodoButtonTap:(id)sender {
  UIButton* button = sender;
  BOOL shouldDelete = button.selected;
  [button setSelected:!shouldDelete];
  if (button.selected) {
    addFavoriteLabel_.text = @"To-Do'd";
  } else {
    addFavoriteLabel_.text = @"To-Do";
  }
  NSString* path = shouldDelete ? kRemoveFavoritePath : kCreateFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  if (shouldDelete) {
    objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
        stamp_.entityObject.entityID, @"entity_id", nil];
    stamp_.entityObject.favorite = nil;
    [stamp_.managedObjectContext save:nil];
  } else {
    objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
        stamp_.entityObject.entityID, @"entity_id",
        stamp_.stampID, @"stamp_id", nil];
  }
  [objectLoader send];
}

- (IBAction)handleSendButtonTap:(id)sender {
  
}

- (IBAction)handleLikeButtonTap:(id)sender {
  UIButton* button = sender;
  BOOL liked = !button.selected;
  button.selected = liked;
  likeLabel_.text = liked ? @"Liked" : @"Like";
  self.numLikes += liked ? 1 : -1;
  NSString* path = liked ? kCreateLikePath : kRemoveLikePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:stamp_.stampID, @"stamp_id", nil];
  
  [objectLoader send];
}

#pragma mark -

- (void)preloadEntityView {
  if (detailViewController_)
    return;

  detailViewController_ = [[Util detailViewControllerForEntity:stamp_.entityObject] retain];
}

- (void)handleTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  if ([addCommentField_ isFirstResponder]) {
    [addCommentField_ resignFirstResponder];
    return;
  }
}

- (void)handlePhotoTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  ShowImageViewController* viewController = [[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil];
  viewController.image = stampPhotoView_.image;
  [self.navigationController pushViewController:viewController animated:YES];
  [viewController release];
}

- (void)handleEntityTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [addCommentField_ resignFirstResponder];
  [self.navigationController pushViewController:detailViewController_ animated:YES];
}

- (void)handleUserImageViewTap:(id)sender {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = stamp_.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

- (void)handleCommentUserImageViewTap:(NSNotification*)notification {
  StampDetailCommentView* commentView = notification.object;
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = commentView.comment.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Comments.

- (void)loadCommentsFromServer {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCommentsPath delegate:self];
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
}

- (void)renderComments {
  NSArray* sortDescriptors = [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES]];
  for (Comment* c in [stamp_.comments sortedArrayUsingDescriptors:sortDescriptors]) {
    if (c.restampID == nil)
      [self addComment:c];
  }
}

- (void)addComment:(Comment*)comment {
  StampDetailCommentView* commentView = nil;
  for (UIView* view in commentsView_.subviews) {
    if ([view isMemberOfClass:[StampDetailCommentView class]]) {
      commentView = (StampDetailCommentView*)view;
      if ([commentView.comment.commentID isEqualToString:comment.commentID])
        return;
    }
  }
  commentView = [[StampDetailCommentView alloc] initWithComment:comment];

  CGRect frame = commentView.frame;
  CGFloat yPos = 0.0;
  frame.size.width = CGRectGetWidth(activityView_.frame);
  for (UIView* view in commentsView_.subviews) {
    if ([view isKindOfClass:[StampDetailCommentView class]])
      yPos += CGRectGetHeight(view.frame);
  }
  frame.origin.y = yPos;
  commentView.frame = frame;
  [commentsView_ addSubview:commentView];
  [commentView release];

  frame = commentsView_.frame;
  frame.size.height += CGRectGetHeight(commentView.frame);
  frame.origin.y -= CGRectGetHeight(commentView.frame);
  commentsView_.frame = frame;

  frame = activityView_.frame;
  frame.size.height += CGRectGetHeight(commentView.frame);
  activityView_.frame = frame;
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  activityGradientLayer_.frame = activityView_.bounds;
  [CATransaction commit];
  [activityGradientLayer_ setNeedsDisplay];
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityView_.frame) + 60);
}

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsMake(0, 0, kKeyboardHeight - 60, 0);
    scrollView_.contentOffset = CGPointMake(0, CGRectGetMaxY(activityView_.frame) - (CGRectGetHeight(scrollView_.frame) - kKeyboardHeight));
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsZero;
  }];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != addCommentField_)
    return YES;

  addCommentField_.hidden = YES;
  currentUserImageView_.hidden = YES;
  [loadingView_ startAnimating];
  [addCommentField_ resignFirstResponder];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateCommentPath delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      addCommentField_.text, @"blurb",
      stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
 
  return NO;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  [loadingView_ stopAnimating];
  addCommentField_.hidden = NO;
  currentUserImageView_.hidden = NO;

	if ([objectLoader.resourcePath isEqualToString:kCreateCommentPath]) {
    Comment* comment = [objects objectAtIndex:0];
    [self addComment:comment];
    [stamp_ addCommentsObject:comment];
    stamp_.numComments = [NSNumber numberWithInt:[stamp_.numComments intValue] + 1];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                        object:stamp_];
    
    addCommentField_.text = nil;
    return;
  } else if ([objectLoader.resourcePath rangeOfString:kCommentsPath].location != NSNotFound) {
    stamp_.numComments = [NSNumber numberWithUnsignedInteger:objects.count];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                        object:stamp_];
    stamp_.comments = [NSSet setWithArray:objects];
    [self renderComments];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];

  if ([objectLoader.resourcePath isEqualToString:kCreateCommentPath]) {
    [loadingView_ stopAnimating];
    addCommentField_.hidden = NO;
    currentUserImageView_.hidden = NO;
    [addCommentField_ becomeFirstResponder];
  }
}

@end
