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
#import <Twitter/Twitter.h>

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
#import "SharedRequestDelegate.h"
#import "WebViewController.h"

NSString* const kRemoveCommentPath = @"/comments/remove.json";
NSString* const kRemoveStampPath = @"/stamps/remove.json";

static const CGFloat kMainCommentFrameMinHeight = 75.0;
static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static NSString* const kCreateLikePath = @"/stamps/likes/create.json";
static NSString* const kRemoveLikePath = @"/stamps/likes/remove.json";
static NSString* const kCreateCommentPath = @"/comments/create.json";
static NSString* const kCommentsPath = @"/comments/show.json";

typedef enum {
  StampDetailActionTypeDeleteComment = 0,
  StampDetailActionTypeRetrySend,
  StampDetailActionTypeDeleteStamp,
  StampDetailActionTypeShare
} StampDetailActionType;

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbar;
- (void)setUpMainContentView;
- (void)addUserGradientBackground;
- (void)addCreditedUsers;
- (void)setNumLikes:(NSUInteger)likes;
- (void)setMainCommentContainerFrame:(CGRect)mainCommentFrame;
- (void)handlePhotoTap:(UITapGestureRecognizer*)recognizer;
- (void)keyboardWillAppear:(NSNotification*)notification;
- (void)keyboardWillDisappear:(NSNotification*)notification;
- (void)handleUserImageViewTap:(id)sender;
- (void)renderComments;
- (void)addComment:(Comment*)comment;
- (void)removeComment:(Comment*)comment;
- (void)loadCommentsFromServer;
- (void)sendAddCommentRequest;
- (void)sendRemoveCommentRequest:(NSString*)commentID;
- (void)showTweetViewController;
- (void)handleURL:(NSURL*)url;
- (void)deleteStampButtonPressed:(id)sender;
- (void)sendDeleteStampRequest;
- (void)setupAlsoStampedBy;
- (NSArray*)alsoStampedByArray;
- (void)alsoStampedByUserImageTapped:(id)sender;

@property (nonatomic, readonly) STImageView* stampPhotoView;
@property (nonatomic, readonly) UIImageView* likeFaceImageView;
@property (nonatomic, readonly) UILabel* numLikesLabel;
@property (nonatomic, assign) NSUInteger numLikes;
@property (nonatomic, assign) BOOL lastCommentAttemptFailed;
@property (nonatomic, retain) NSMutableArray* commentViews;
@end

@implementation StampDetailViewController

@synthesize mainCommentContainer = mainCommentContainer_;
@synthesize scrollView = scrollView_;
@synthesize commentsView = commentsView_;
@synthesize activityView = activityView_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize commenterImageView = commenterImageView_;
@synthesize commenterNameLabel = commenterNameLabel_;
@synthesize stampedLabel = stampedLabel_;
@synthesize addFavoriteButton = addFavoriteButton_;
@synthesize addFavoriteLabel = addFavoriteLabel_;
@synthesize likeButton = likeButton_;
@synthesize likeLabel = likeLabel_;
@synthesize shareLabel = shareLabel_;
@synthesize shareButton = shareButton_;
@synthesize stampLabel = stampLabel_;
@synthesize stampButton = stampButton_;
@synthesize stampPhotoView = stampPhotoView_;
@synthesize likeFaceImageView = likeFaceImageView_;
@synthesize numLikesLabel = numLikesLabel_;
@synthesize numLikes = numLikes_;
@synthesize timestampLabel = timestampLabel_;
@synthesize titleLabel = titleLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize subtitleLabel = subtitleLabel_;
@synthesize currentUserImageView = currentUserImageView_;
@synthesize commentTextField = commentTextField_;
@synthesize sendButton = sendButton_;
@synthesize sendIndicator = sendIndicator_;
@synthesize lastCommentAttemptFailed = lastCommentAttemptFailed_;
@synthesize commentViews = commentViews_;
@synthesize alsoStampedByLabel = alsoStampedByLabel_;
@synthesize alsoStampedByContainer = alsoStampedByContainer_;
@synthesize alsoStampedByScrollView = alsoStampedByScrollView_;

- (id)initWithStamp:(Stamp*)stamp {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    stamp_ = [stamp retain];
    self.commentViews = [NSMutableArray array];
  }
  return self;
}

- (void)dealloc {
  [Stamp.managedObjectContext refreshObject:stamp_ mergeChanges:NO];
  [stamp_ release];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.categoryImageView = nil;
  self.subtitleLabel = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteLabel = nil;
  self.likeButton = nil;
  self.likeLabel = nil;
  self.shareLabel = nil;
  self.shareButton = nil;
  self.stampLabel = nil;
  self.stampButton = nil;
  self.timestampLabel = nil;
  self.currentUserImageView = nil;
  self.commentTextField = nil;
  self.sendButton = nil;
  self.sendIndicator = nil;
  self.commentViews = nil;
  self.alsoStampedByContainer = nil;
  self.alsoStampedByLabel = nil;
  self.alsoStampedByScrollView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [commentTextField_ resignFirstResponder];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(keyboardWillAppear:)
                                               name:UIKeyboardWillShowNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(keyboardWillDisappear:)
                                               name:UIKeyboardWillHideNotification
                                             object:nil];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  stampPhotoView_.imageURL = stamp_.imageURL;
}

- (void)viewDidLoad {
  [super viewDidLoad];

  [self setUpToolbar];
  [self setUpHeader];

  if ([[AccountManager sharedManager].currentUser.userID isEqualToString:stamp_.user.userID]) {
    UIBarButtonItem* rightButton = [[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                    style:UIBarButtonItemStylePlain
                                                                   target:self
                                                                   action:@selector(deleteStampButtonPressed:)];
    self.navigationItem.rightBarButtonItem = rightButton;
    [rightButton release];
  }

  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:stamp_.entityObject.title
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];

  activityView_.layer.shadowOpacity = 0.1;
  activityView_.layer.shadowOffset = CGSizeMake(0, 1);
  activityView_.layer.shadowRadius = 2;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  mainCommentContainer_.layer.shadowOpacity = 0.1;
  mainCommentContainer_.layer.shadowOffset = CGSizeMake(0, 0);
  mainCommentContainer_.layer.shadowRadius = 2;
  mainCommentContainer_.layer.shadowPath =
      [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;

  currentUserImageView_.imageURL = [AccountManager sharedManager].currentUser.profileImageURL;
  
  [self setupAlsoStampedBy];
  [self setUpMainContentView];
  [self renderComments];
  [self loadCommentsFromServer];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.categoryImageView = nil;
  self.subtitleLabel = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteButton = nil;
  self.addFavoriteLabel = nil;
  self.likeButton = nil;
  self.likeLabel = nil;
  self.shareLabel = nil;
  self.shareButton = nil;
  self.stampLabel = nil;
  self.stampButton = nil;
  self.currentUserImageView = nil;
  self.commentTextField = nil;
  self.timestampLabel = nil;
  self.sendButton = nil;
  self.sendIndicator = nil;
  self.alsoStampedByContainer = nil;
  self.alsoStampedByLabel = nil;
  self.alsoStampedByScrollView = nil;
}

- (void)setUpHeader {
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  CGSize stringSize = [stamp_.entityObject.title sizeWithFont:[UIFont fontWithName:fontString size:fontSize]
                                                     forWidth:270
                                                lineBreakMode:UILineBreakModeTailTruncation];

  titleLabel_.font = [UIFont fontWithName:fontString size:fontSize];
  titleLabel_.text = stamp_.entityObject.title;
  titleLabel_.textColor = [UIColor stampedDarkGrayColor];

  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                17 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)stamp_.user.stampImage.CGImage;
  [scrollView_.layer insertSublayer:stampLayer above:titleLabel_.layer];
  [stampLayer release];
  
  categoryImageView_.image = stamp_.entityObject.categoryImage;
  subtitleLabel_.text = stamp_.entityObject.subtitle;
  subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
  subtitleLabel_.textColor = [UIColor stampedGrayColor];
}

- (void)setUpToolbar {
  if (stamp_.entityObject.favorite) {
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
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds), CGRectGetMaxY(activityView_.frame) + 10);
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  activityGradientLayer_.frame = activityView_.bounds;
  [CATransaction commit];
  if (!alsoStampedByContainer_.hidden) {
    CGRect stampedByFrame = alsoStampedByContainer_.frame;
    stampedByFrame.origin.y = CGRectGetMaxY(activityView_.frame) + 17;
    alsoStampedByContainer_.frame = stampedByFrame;
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(alsoStampedByContainer_.frame) + 10);
  } else {
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(activityView_.frame) + 10);
  }
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

- (void)setupAlsoStampedBy {
  NSArray* stampsArray = [self alsoStampedByArray];
  if (stampsArray.count == 0) {
    alsoStampedByContainer_.hidden = YES;
    return;
  }
  
  alsoStampedByContainer_.hidden = NO;
  alsoStampedByScrollView_.contentSize = CGSizeMake(alsoStampedByScrollView_.frame.size.width,
                                                    alsoStampedByScrollView_.frame.size.height);
  CGRect userImgFrame = CGRectMake(0.0, 0.0, 43.0, 43.0);

  Stamp* s = nil;
  NSUInteger pageNum = 1;
  for (NSUInteger i = 0; i < stampsArray.count; ++i) {
    s = [stampsArray objectAtIndex:i];
    UserImageView* userImage = [[UserImageView alloc] initWithFrame:userImgFrame];
    
    if (i > 1 && i % 6 == 0) {
      alsoStampedByScrollView_.contentSize =
          CGSizeMake(alsoStampedByScrollView_.contentSize.width + alsoStampedByScrollView_.frame.size.width,
                     alsoStampedByScrollView_.contentSize.height);
      pageNum++;
    }

    CGFloat xOffset = i * (userImgFrame.size.width + 7.0) + 10.0 * (pageNum - 1) + 9.0;

    userImage.frame = CGRectOffset(userImgFrame, xOffset, 5);
    userImage.contentMode = UIViewContentModeCenter;
    userImage.layer.shadowOffset = CGSizeMake(0, 1);
    userImage.layer.shadowOpacity = 0.2;
    userImage.layer.shadowRadius = 1.75;
    userImage.imageURL = s.user.profileImageURL;
    userImage.enabled = YES;
    [userImage addTarget:self
                  action:@selector(alsoStampedByUserImageTapped:)
        forControlEvents:UIControlEventTouchUpInside];
    userImage.tag = i;
    [alsoStampedByScrollView_ addSubview:userImage];
    [userImage release];
  }
}

- (NSArray*)alsoStampedByArray {
  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
  NSArray* stampsArray = [stamp_.entityObject.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  NSString* excludedUserID = stamp_.user.userID;
  NSPredicate* p = [NSPredicate predicateWithFormat:@"temporary == NO AND deleted == NO AND user.userID != %@", excludedUserID];
  return [stampsArray filteredArrayUsingPredicate:p];
}

- (void)alsoStampedByUserImageTapped:(id)sender {
  Stamp* stamp = (Stamp*)[[self alsoStampedByArray] objectAtIndex:[sender tag]];
  StampDetailViewController* vc = [[StampDetailViewController alloc] initWithStamp:stamp];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
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

  timestampLabel_.text = [Util shortUserReadableTimeSinceDate:stamp_.created];
  [timestampLabel_ sizeToFit];
  timestampLabel_.frame = CGRectMake(310 - CGRectGetWidth(timestampLabel_.frame) - 10,
                                     10,
                                     CGRectGetWidth(timestampLabel_.frame),
                                     CGRectGetHeight(timestampLabel_.frame));
  
  
  TTTAttributedLabel* commentLabel = [[TTTAttributedLabel alloc] initWithFrame:CGRectZero];
  commentLabel.delegate = self;
  commentLabel.userInteractionEnabled = YES;
  UIFont* commentFont = [UIFont fontWithName:@"Helvetica" size:14];
  commentLabel.dataDetectorTypes = UIDataDetectorTypeLink;
  NSMutableDictionary* linkAttributes = [NSMutableDictionary dictionary];
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica", 14, NULL);
  [linkAttributes setValue:(id)font forKey:(NSString*)kCTFontAttributeName];
  [linkAttributes setValue:(id)[UIColor stampedGrayColor].CGColor
                    forKey:(NSString*)kCTForegroundColorAttributeName];
  CFRelease(font);
  commentLabel.linkAttributes = [NSDictionary dictionaryWithDictionary:linkAttributes];
  commentLabel.font = commentFont;
  commentLabel.lineBreakMode = UILineBreakModeWordWrap;
  commentLabel.textColor = [UIColor stampedBlackColor];
  commentLabel.text = stamp_.blurb;
  if (stamp_.blurb.length > 0) {
    NSError* error = NULL;
    NSRegularExpression* regex = [NSRegularExpression
                                  regularExpressionWithPattern:@"@(\\w+)"
                                  options:NSRegularExpressionCaseInsensitive
                                  error:&error];
    [regex enumerateMatchesInString:stamp_.blurb
                            options:0
                              range:NSMakeRange(0, stamp_.blurb.length)
                         usingBlock:^(NSTextCheckingResult* match, NSMatchingFlags flags, BOOL* stop){
                           [commentLabel addLinkToURL:[NSURL URLWithString:[stamp_.blurb substringWithRange:match.range]]
                                             withRange:match.range];
                         }];
  }
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
                                       200, floorf(200 * (height / width)));
    CGFloat addedHeight = CGRectGetHeight(stampPhotoView_.bounds);
    mainCommentFrame.size.height += addedHeight;
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
  [self addCreditedUsers];
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

- (void)addCreditedUsers {
  if (!stamp_.credits.count)
    return;

  User* creditedUser = [stamp_.credits anyObject];
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
  
  TTTAttributedLabel* creditLabel = [[TTTAttributedLabel alloc] initWithFrame:CGRectZero];
  creditLabel.delegate = self;
  creditLabel.userInteractionEnabled = YES;
  creditLabel.textColor = [UIColor stampedGrayColor];
  creditLabel.font = [UIFont fontWithName:@"Helvetica" size:12.0];
  creditLabel.dataDetectorTypes = UIDataDetectorTypeLink;
  NSMutableDictionary* linkAttributes = [NSMutableDictionary dictionary];
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  [linkAttributes setValue:(id)font forKey:(NSString*)kCTFontAttributeName];
  CFRelease(font);
  creditLabel.linkAttributes = [NSDictionary dictionaryWithDictionary:linkAttributes];
  if (stamp_.credits.count == 1) {
    creditLabel.text = [NSString stringWithFormat:@"Credit to %@", creditedUser.screenName];
    [creditLabel addLinkToURL:[NSURL URLWithString:[NSString stringWithFormat:@"%@", creditedUser.userID]]
                    withRange:[creditLabel.text rangeOfString:creditedUser.screenName
                                                      options:NSBackwardsSearch]];
  } else {
    NSString* others = nil;
    if (stamp_.credits.count - 1 == 0)
      others = @"1 other";
    else
      others = [NSString stringWithFormat:@"%d others", stamp_.credits.count - 1];
    creditLabel.text = [NSString stringWithFormat:@"Credit to %@ and %@", creditedUser.screenName, others];
    [creditLabel addLinkToURL:[NSURL URLWithString:[NSString stringWithFormat:@"%@", creditedUser.userID]]
                    withRange:[creditLabel.text rangeOfString:creditedUser.screenName
                                                      options:NSBackwardsSearch]];
    NSMutableArray* otherUsers = [NSMutableArray array];
    for (User* user in stamp_.credits) {
      if (user == creditedUser)
        continue;
      
      [otherUsers addObject:user.userID];
    }
    [creditLabel addLinkToURL:[NSURL URLWithString:[otherUsers componentsJoinedByString:@","]]
                    withRange:[creditLabel.text rangeOfString:others options:NSBackwardsSearch]];
  }
  [creditLabel sizeToFit];
  creditLabel.frame = CGRectMake(CGRectGetMaxX(secondStampLayer.frame) + 5,
                                 CGRectGetMinY(secondStampLayer.frame) - 1,
                                 CGRectGetWidth(creditLabel.frame),
                                 CGRectGetHeight(creditLabel.frame));
  [mainCommentContainer_ addSubview:creditLabel];
  [creditLabel release];
}

#pragma mark - TTTAttributedLabelDelegate methods.

- (void)attributedLabel:(TTTAttributedLabel*)label didSelectLinkWithURL:(NSURL*)url {
  [self handleURL:url];
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

- (IBAction)handleShareButtonTap:(id)sender {
  NSString* tweetMsg = nil;
  if ([TWTweetComposeViewController canSendTweet] &&
      [AccountManager.sharedManager.currentUser.screenName isEqualToString:stamp_.user.screenName]) {
    tweetMsg = @"Share to Twitter...";
  }

  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:nil
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:nil
                                             otherButtonTitles:@"Copy link", tweetMsg, nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  sheet.tag = StampDetailActionTypeShare;
  [sheet showInView:self.view];
  return;
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

- (void)deleteStampButtonPressed:(id)sender {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure you want to delete this stamp?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Delete"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  sheet.tag = StampDetailActionTypeDeleteStamp;
  [sheet showInView:self.view];
  return;
}

- (void)handlePhotoTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;
  ShowImageViewController* viewController = [[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil];
  viewController.image = stampPhotoView_.image;
  [self.navigationController pushViewController:viewController animated:YES];
  [viewController release];
}

- (IBAction)handleEntityTap:(id)sender {
  // Fix for long back button titles overlapping the Stamped logo.
  NSString* title = self.navigationItem.backBarButtonItem.title;
  CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]];
  if (titleSize.width > 87) {
    while (titleSize.width > 87) {
      if ([title isEqualToString:self.navigationItem.backBarButtonItem.title])
        title = [[title substringToIndex:title.length - 1] stringByAppendingString:@"…"];
      else
        title = [[title substringToIndex:title.length - 2] stringByAppendingString:@"…"];
        // -2 because we've already appended the ellipsis.
      titleSize = [title sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]];
    }
    NSLog(@"back button text size: %f x %f", titleSize.width, titleSize.height);
    UIBarButtonItem *backButton = [[UIBarButtonItem alloc] initWithTitle:title 
                                                                   style:UIBarButtonItemStyleBordered
                                                                  target:nil
                                                                  action:nil];
    [self.navigationItem setBackBarButtonItem: backButton];
    [backButton release];
  }
  
  UIViewController* detailViewController = [Util detailViewControllerForEntity:stamp_.entityObject];
  [self.navigationController pushViewController:detailViewController animated:YES];
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

#pragma mark - StampDetailCommentViewDelegate methods.

- (BOOL)commentViewShouldBeginEditing:(StampDetailCommentView*)commentView {
  for (StampDetailCommentView* view in commentViews_)
    view.editing = NO;

  User* currentUser = [AccountManager sharedManager].currentUser;
  if ([stamp_.user.userID isEqualToString:currentUser.userID] || [commentView.comment.user.userID isEqualToString:currentUser.userID])
    return YES;

  return NO;
}

- (void)commentViewUserImageTapped:(StampDetailCommentView*)commentView {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = commentView.comment.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

- (void)commentViewDeleteButtonPressed:(StampDetailCommentView*)commentView {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Are you sure you want to delete this comment?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Delete"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  sheet.tag = StampDetailActionTypeDeleteComment;
  [sheet showInView:self.view];
  return;
}

- (void)commentView:(StampDetailCommentView*)commentView didSelectLinkWithURL:(NSURL*)url {
  [self handleURL:url];
}

#pragma mark - Comments.

- (void)loadCommentsFromServer {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCommentsPath delegate:self];
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
}

- (void)renderComments {
  NSArray* sortDescriptors = [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"created"
                                                                                    ascending:YES]];
  for (Comment* c in [stamp_.comments sortedArrayUsingDescriptors:sortDescriptors]) {
    if (c.restampID == nil)
      [self addComment:c];
  }
  NSArray* commentIDs = [stamp_.comments valueForKeyPath:@"@distinctUnionOfObjects.commentID"];
  NSArray* viewComments = [commentViews_ valueForKeyPath:@"@distinctUnionOfObjects.comment"];
  for (Comment* c in viewComments) {
    if (c.restampID == nil && ![commentIDs containsObject:c.commentID])
      [self removeComment:c];
  }
}

- (void)addComment:(Comment*)comment {
  for (StampDetailCommentView* view in commentViews_) {
    if ([view.comment.commentID isEqualToString:comment.commentID])
      return;
  }

  StampDetailCommentView* commentView = [[StampDetailCommentView alloc] initWithComment:comment];

  commentView.delegate = self;
  CGRect frame = commentView.frame;
  CGFloat yPos = 0.0;
  frame.size.width = CGRectGetWidth(activityView_.frame);
  for (StampDetailCommentView* view in commentViews_)
    yPos += CGRectGetHeight(view.frame);

  frame.origin.y = yPos;
  commentView.frame = frame;
  [commentsView_ addSubview:commentView];
  [commentView release];
  [commentViews_ addObject:commentView];

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
  if (!alsoStampedByContainer_.hidden) {
    CGRect stampedByFrame = alsoStampedByContainer_.frame;
    stampedByFrame.origin.y = CGRectGetMaxY(activityView_.frame) + 17;
    alsoStampedByContainer_.frame = stampedByFrame;
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(alsoStampedByContainer_.frame) + 10);
  } else {
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(activityView_.frame) + 10);
  }
}

- (void)removeComment:(Comment*)comment {
  StampDetailCommentView* commentView = nil;
  for (StampDetailCommentView* view in commentViews_) {
    if ([view.comment.commentID isEqualToString:comment.commentID]) {
      commentView = view;
      break;
    }
  }

  for (StampDetailCommentView* view in commentViews_) {
    if ([commentViews_ indexOfObject:view] <= [commentViews_ indexOfObject:commentView])
      continue;
    CGRect frame = view.frame;
    frame.origin.y -= CGRectGetHeight(commentView.frame);
    view.frame = frame;
  }
  
  [commentViews_ removeObject:commentView];
  CGRect frame = commentsView_.frame;
  frame.size.height -= CGRectGetHeight(commentView.frame);
  frame.origin.y += CGRectGetHeight(commentView.frame);
  commentsView_.frame = frame;
  
  frame = activityView_.frame;
  frame.size.height -= CGRectGetHeight(commentView.frame);
  [commentView removeFromSuperview];
  activityView_.frame = frame;
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  activityGradientLayer_.frame = activityView_.bounds;
  [CATransaction commit];
  [activityGradientLayer_ setNeedsDisplay];
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  if (!alsoStampedByContainer_.hidden) {
    CGRect stampedByFrame = alsoStampedByContainer_.frame;
    stampedByFrame.origin.y = CGRectGetMaxY(activityView_.frame) + 17;
    alsoStampedByContainer_.frame = stampedByFrame;
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(alsoStampedByContainer_.frame) + 10);
  } else {
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(activityView_.frame) + 10);
  }
  
  stamp_.numComments = [NSNumber numberWithInt:[stamp_.numComments intValue] - 1];
  [stamp_.managedObjectContext save:NULL];
  [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                      object:stamp_];
}

- (void)handleURL:(NSURL*)url {
  if ([url.scheme isEqualToString:@"http"]) {
    WebViewController* vc = [[WebViewController alloc] initWithURL:url];
    [self.navigationController pushViewController:vc animated:YES];
    [vc release];
    return;
  }

  NSString* urlString = url.absoluteString;
  User* user = nil;
  if ([urlString hasPrefix:@"@"]) {
    NSString* screenName = [urlString substringFromIndex:1];
    user = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", screenName]]; 
  } else if (urlString.length == 24) {
    NSString* userID = url.absoluteString;
    user = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"userID == %@", userID]];
  }
  if (!user)
    return;

  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - Keyboard notifications.

- (void)keyboardWillAppear:(NSNotification*)notification {
  if (self.modalViewController)
    return;

  CGRect keyboardFrame = [[[notification userInfo] valueForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
  CGFloat scrollHeight = CGRectGetHeight(self.view.frame) - CGRectGetHeight(keyboardFrame);
  if (!alsoStampedByContainer_.hidden) {
    CGRect stampedByFrame = alsoStampedByContainer_.frame;
    stampedByFrame.origin.y = CGRectGetMaxY(activityView_.frame) + 17;
    alsoStampedByContainer_.frame = stampedByFrame;
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(alsoStampedByContainer_.frame) + 10);
  } else {
    scrollView_.contentSize = CGSizeMake(CGRectGetWidth(scrollView_.bounds),
                                         CGRectGetMaxY(activityView_.frame) + 10);
  }
  
  CGFloat contentHeight = alsoStampedByContainer_.hidden ?
      CGRectGetMaxY(activityView_.frame) + 10 : CGRectGetMaxY(alsoStampedByContainer_.frame) + 10;

  [UIView animateWithDuration:0.3
                        delay:0.0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     scrollView_.frame = CGRectMake(0, 0, 320, scrollHeight);
                     scrollView_.contentOffset = CGPointMake(0, contentHeight - scrollHeight);
                     commentTextField_.frame = CGRectOffset(CGRectInset(commentTextField_.frame, 27, 0), -27, 0);
                     sendButton_.alpha = 1.0;
                   }
                   completion:nil];
}

- (void)keyboardWillDisappear:(NSNotification*)notification {
  if (self.modalViewController)
    return;

  CGFloat scrollHeight = CGRectGetHeight(self.view.frame) - CGRectGetHeight(bottomToolbar_.frame);
  [UIView animateWithDuration:0.3
                        delay:0.0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     scrollView_.frame = CGRectMake(0, 0, 320, scrollHeight);
                     commentTextField_.frame = CGRectOffset(CGRectInset(commentTextField_.frame, -27, 0), 27, 0);
                     sendButton_.alpha = 0.0;
                   }
                   completion:nil];
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (actionSheet.tag == StampDetailActionTypeRetrySend) {
    if (buttonIndex == 0) {  // Try again.
      [sendButton_ setBackgroundImage:[UIImage imageNamed:@"green_button_bg"] forState:UIControlStateNormal];
      [sendButton_ setImage:nil forState:UIControlStateNormal];
      lastCommentAttemptFailed_ = NO;
      [self sendAddCommentRequest];
    }
  } else if (actionSheet.tag == StampDetailActionTypeDeleteComment) {
    if (buttonIndex == 0) {  // DELETE.
      Comment* comment = nil;
      for (StampDetailCommentView* view in commentViews_) {
        if (view.editing)
          comment = view.comment;
      }
      if (comment) {
        [self removeComment:comment];
        [self sendRemoveCommentRequest:comment.commentID];
      }
    } else { // Cancel.
      for (StampDetailCommentView* view in commentViews_)
        view.editing = NO;
    }
  } else if (actionSheet.tag == StampDetailActionTypeDeleteStamp && buttonIndex == 0) {
    if (stamp_.entityObject.stamps.count > 1) {
      NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
      NSMutableArray* sortedStamps =
          [NSMutableArray arrayWithArray:[[stamp_.entityObject.stamps allObjects] sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]]];
      [sortedStamps removeObject:stamp_];
      Stamp* latestStamp = [sortedStamps objectAtIndex:0];
      stamp_.entityObject.mostRecentStampDate = latestStamp.created;
    }
    
    Favorite* fave = [Favorite objectWithPredicate:
        [NSPredicate predicateWithFormat:@"entityObject.entityID == %@", stamp_.entityObject.entityID]];
    fave.complete = [NSNumber numberWithBool:NO];

    stamp_.user.numStamps = [NSNumber numberWithInteger:(stamp_.user.numStamps.integerValue - 1)];
    stamp_.user.numStampsLeft = [NSNumber numberWithInteger:(stamp_.user.numStampsLeft.integerValue + 1)];

    [self sendDeleteStampRequest];
    [Stamp.managedObjectContext deleteObject:stamp_];
    [Stamp.managedObjectContext save:NULL];

    [self.navigationController popViewControllerAnimated:YES];
  } else if (actionSheet.tag == StampDetailActionTypeShare) {
    BOOL canTweet = NO;
    if ([TWTweetComposeViewController canSendTweet] &&
        [AccountManager.sharedManager.currentUser.screenName isEqualToString:stamp_.user.screenName]) {
      canTweet = YES;
    }
    if (buttonIndex == 0) {  // Copy link...
      [UIPasteboard generalPasteboard].URL = [NSURL URLWithString:stamp_.URL];
    } else if (buttonIndex == 1 && canTweet) {  // Twitter or cancel depending...
      [self showTweetViewController];
    }
  }
}

- (void)showTweetViewController {
  TWTweetComposeViewController* twitter = [[[TWTweetComposeViewController alloc] init] autorelease];
  NSString* blurb = [NSString stringWithFormat:@"%@. \u201c%@\u201d", stamp_.entityObject.title, stamp_.blurb];
  if (stamp_.blurb.length == 0)
    blurb = [stamp_.entityObject.title stringByAppendingString:@"."];
  
  NSString* substring = [blurb substringToIndex:MIN(blurb.length, 104)];
  if (blurb.length > substring.length)
    blurb = [substring stringByAppendingString:@"..."];
  
  // Stamped: [blurb] [link]
  [twitter setInitialText:[NSString stringWithFormat:@"Stamped: %@", blurb]];
  [twitter addURL:[NSURL URLWithString:stamp_.URL]];
  
  if ([TWTweetComposeViewController canSendTweet]) {
    [self presentViewController:twitter animated:YES completion:nil];
  }
  
  twitter.completionHandler = ^(TWTweetComposeViewControllerResult result) {
    [self dismissModalViewControllerAnimated:YES];
  };
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  [sendButton_ setBackgroundImage:[UIImage imageNamed:@"green_button_bg"] forState:UIControlStateNormal];
  [sendButton_ setTitle:@"Send" forState:UIControlStateNormal];
  [sendButton_ setImage:nil forState:UIControlStateNormal];
  lastCommentAttemptFailed_ = NO;
  NSString* result = [textField.text stringByReplacingCharactersInRange:range withString:string];
  sendButton_.enabled = result.length > 0;
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  sendButton_.enabled = commentTextField_.text.length > 0;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

- (IBAction)sendButtonPressed:(id)sender {
  if (lastCommentAttemptFailed_) {
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"There was a problem adding your comment."
                                                        delegate:self
                                               cancelButtonTitle:@"Cancel"
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Try Again", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    sheet.tag = StampDetailActionTypeRetrySend;
    [sheet showInView:self.view];
    return;
  }

  [self sendAddCommentRequest];
}

- (void)sendDeleteStampRequest {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kRemoveStampPath 
                                                                    delegate:[SharedRequestDelegate sharedDelegate]];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = mapping;
  objectLoader.params = [NSDictionary dictionaryWithObject:stamp_.stampID forKey:@"stamp_id"];
  [objectLoader send];
}

- (void)sendRemoveCommentRequest:(NSString*)commentID {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kRemoveCommentPath 
                                                                    delegate:[SharedRequestDelegate sharedDelegate]];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObject:commentID forKey:@"comment_id"];
  [objectLoader send];
}

- (void)sendAddCommentRequest {
  [sendButton_ setTitle:nil forState:UIControlStateNormal];
  [sendButton_ setImage:nil forState:UIControlStateNormal];
  [sendIndicator_ startAnimating];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateCommentPath delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
                         commentTextField_.text, @"blurb",
                         stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath isEqualToString:kCreateCommentPath]) {
    lastCommentAttemptFailed_ = NO;
    [sendButton_ setTitle:@"Send" forState:UIControlStateNormal];
    [sendIndicator_ stopAnimating];
    commentTextField_.text = nil;
    [commentTextField_ resignFirstResponder];
    Comment* comment = [objects objectAtIndex:0];
    [self addComment:comment];
    [stamp_ addCommentsObject:comment];
    stamp_.numComments = [NSNumber numberWithInt:[stamp_.numComments intValue] + 1];
    [stamp_.managedObjectContext save:NULL];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                        object:stamp_];
    return;
  } else if ([objectLoader.resourcePath rangeOfString:kCommentsPath].location != NSNotFound) {
    stamp_.numComments = [NSNumber numberWithUnsignedInteger:objects.count];
    [stamp_ removeComments:stamp_.comments];
    [stamp_ addComments:[NSSet setWithArray:objects]];
    [Stamp.managedObjectContext save:NULL];
    [self renderComments];
  }
  [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                      object:stamp_];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];

  if ([objectLoader.resourcePath isEqualToString:kCreateCommentPath]) {
    // Problem with sending the comment...
    lastCommentAttemptFailed_ = YES;
    [sendButton_ setTitle:nil forState:UIControlStateNormal];
    [sendButton_ setBackgroundImage:[UIImage imageNamed:@"comment_fail_button_bg"] forState:UIControlStateNormal];
    [sendButton_ setImage:[UIImage imageNamed:@"comment_fail_icon"] forState:UIControlStateNormal];
    [sendIndicator_ stopAnimating];
  }
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [super scrollViewDidScroll:scrollView];
  for (StampDetailCommentView* view in commentViews_)
    view.editing = NO;
}

@end
