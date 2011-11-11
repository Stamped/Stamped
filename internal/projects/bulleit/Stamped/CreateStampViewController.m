//
//  CreateStampViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampViewController.h"

#import <CoreText/CoreText.h>
#import <MobileCoreServices/UTCoreTypes.h>
#import <RestKit/CoreData/CoreData.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "STCreditTextField.h"
#import "EditEntityViewController.h"
#import "DetailedEntity.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Favorite.h"
#import "GTMOAuthAuthentication.h"
#import "GTMOAuthViewControllerTouch.h"
#import "STNavigationBar.h"
#import "Notifications.h"
#import "Stamp.h"
#import "SearchResult.h"
#import "StampedAppDelegate.h"
#import "UserImageView.h"
#import "Util.h"
#import "User.h"
#import "UIColor+Stamped.h"
#import "STOAuthViewController.h"
#import "Alerts.h"
#import "SharedRequestDelegate.h"

static NSString* const kTwitterUpdateStatusPath = @"/statuses/update.json";
static NSString* const kCreateStampPath = @"/stamps/create.json";
static NSString* const kCreateEntityPath = @"/entities/create.json";
static NSString* const kStampPhotoURLPath = @"http://static.stamped.com/stamps/";
static NSString* const kStampLogoURLPath = @"http://static.stamped.com/logos/";
static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kTwitterFollowersURI = @"/followers/ids.json";
static NSString* const kFacebookFriendsURI = @"/me/friends";
static NSString* const kStampedTwitterLinkPath = @"/account/linked/twitter/update.json";
static NSString* const kStampedTwitterRemovePath = @"/account/linked/twitter/remove.json";
static NSString* const kStampedTwitterFollowersPath = @"/account/linked/twitter/followers.json";
static NSString* const kStampedFacebookLinkPath = @"/account/linked/facebook/update.json";
static NSString* const kStampedFacebookRemovePath = @"/account/linked/facebook/remove.json";
static NSString* const kStampedFacebookFriendsPath = @"/account/linked/facebook/followers.json";

@interface CreateStampViewController () {
}
- (void)editorDoneButtonPressed:(id)sender;
- (void)editorCameraButtonPressed:(id)sender;
- (void)takePhotoButtonPressed:(id)sender;
- (void)choosePhotoButtonPressed:(id)sender;
- (void)deletePhotoButtonPressed:(id)sender;
- (void)adjustTextViewContentSize;
- (void)sendSaveStampRequest;
- (void)sendSaveEntityRequest;
- (void)sendTweetRequest:(Stamp*)stamp;
- (void)dismissSelf;
- (void)addStampPhotoView;
- (void)restoreViewState;
- (void)addStampsRemainingLayer;

- (void)signInToTwitter;
- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error;

- (void)fetchCurrentUser;
- (void)signInToFacebook;
- (GTMOAuthAuthentication*)createAuthentication;

@property (nonatomic, retain) UIImage* stampPhoto;
@property (nonatomic, retain) UIButton* takePhotoButton;
@property (nonatomic, retain) UIButton* deletePhotoButton;
@property (nonatomic, retain) UIImageView* stampPhotoView;
@property (nonatomic, copy) NSString* reasoningText;
@property (nonatomic, copy) NSString* creditedUserText;
@property (nonatomic, assign) BOOL savePhoto;
@property (nonatomic, retain) UIResponder* firstResponder;
@property (nonatomic, readonly) CATextLayer* stampsRemainingLayer;
@property (nonatomic, retain) RKClient* twitterClient;
@property (nonatomic, retain) GTMOAuthAuthentication* twitterAuth;
@property (nonatomic, retain) id objectToStamp;
@property (nonatomic, readonly) UIView* editingMask;
@property (nonatomic, retain) STCreditPickerController* creditPickerController;
@property (nonatomic, retain) DetailedEntity* detailedEntity;
@end

@implementation CreateStampViewController

@synthesize entityObject = entityObject_;
@synthesize creditedUser = creditedUser_;
@synthesize newEntity = newEntity_;
@synthesize detailedEntity = detailedEntity_;
@synthesize fbClient = fbClient_;

@synthesize scrollView = scrollView_;
@synthesize titleLabel = titleLabel_;
@synthesize detailLabel = detailLabel_;
@synthesize reasoningLabel = reasoningLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize userImageView = userImageView_;
@synthesize ribbonedContainerView = ribbonedContainerView_;
@synthesize reasoningTextView = reasoningTextView_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize spinner = spinner_;
@synthesize stampItButton = stampItButton_;
@synthesize creditTextField = creditTextField_;
@synthesize editButton = editButton_;
@synthesize disclosureButton = disclosureButton_;
@synthesize mainCommentContainer = mainCommentContainer_;
@synthesize backgroundImageView = backgroundImageView_;
@synthesize stampPhoto = stampPhoto_;
@synthesize takePhotoButton = takePhotoButton_;
@synthesize savePhoto = savePhoto_;
@synthesize stampPhotoView = stampPhotoView_;
@synthesize deletePhotoButton = deletePhotoButton_;
@synthesize reasoningText = reasoningText_;
@synthesize creditedUserText = creditedUserText_;
@synthesize firstResponder = firstResponder_;
@synthesize stampsRemainingLayer = stampsRemainingLayer_;
@synthesize tweetButton = tweetButton_;
@synthesize twitterAuth = twitterAuth_;
@synthesize twitterClient = twitterClient_;
@synthesize shareLabel = shareLabel_;
@synthesize editingMask = editingMask_;
@synthesize creditPickerController = creditPickerController_;
@synthesize fbButton = fbButton_;
@synthesize objectToStamp = objectToStamp_;
@synthesize signInTwitterActivityIndicator = signInTwitterActivityIndicator_;
@synthesize signInFacebookActivityIndicator = signInFacebookActivityIndicator_;

- (id)initWithEntityObject:(Entity*)entityObject {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    creditPickerController_ = [[STCreditPickerController alloc] init];
    creditPickerController_.delegate = self;

    self.entityObject = entityObject;
    self.objectToStamp = entityObject;
  }
  return self;
}

- (id)initWithEntityObject:(Entity*)entityObject creditedTo:(User*)user {
  self = [self initWithEntityObject:entityObject];
  if (self) {
    self.creditedUser = user;
  }
  return self;
}

- (id)initWithSearchResult:(SearchResult*)searchResult {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    creditPickerController_ = [[STCreditPickerController alloc] init];
    creditPickerController_.delegate = self;

    if (!searchResult.entityID && !searchResult.searchID) {
      newEntity_ = YES;
      self.detailedEntity = [DetailedEntity object];
      detailedEntity_.title = searchResult.title;
      self.objectToStamp = detailedEntity_;
    } else {
      self.objectToStamp = searchResult;
    }
  }
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [twitterClient_.requestQueue cancelRequestsWithDelegate:self];
  if ([fbClient_.sessionDelegate isEqual:self])
    fbClient_.sessionDelegate = nil;
  [[NSNotificationCenter defaultCenter] removeObserver:self]; 
  self.entityObject = nil;
  self.creditedUser = nil;
  self.stampPhoto = nil;
  self.reasoningText = nil;
  self.creditedUserText = nil;
  self.firstResponder = nil;
  self.objectToStamp = nil;
  self.scrollView = nil;
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.bottomToolbar = nil;
  self.spinner = nil;
  self.stampItButton = nil;
  self.creditTextField.delegate = nil;
  self.creditTextField = nil;
  self.editButton = nil;
  self.mainCommentContainer = nil;
  self.backgroundImageView = nil;
  self.takePhotoButton = nil;
  self.deletePhotoButton = nil;
  self.twitterAuth = nil;
  self.twitterClient = nil;
  self.disclosureButton = nil;
  self.creditPickerController.delegate = nil;
  self.creditPickerController = nil;
  self.detailedEntity = nil;
  stampsRemainingLayer_ = nil;
  self.fbClient = nil;
  self.fbButton = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"New Stamp"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
  
  self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  User* currentUser = [AccountManager sharedManager].currentUser;
  self.userImageView.imageURL = currentUser.profileImageURL;
  scrollView_.contentSize = self.view.bounds.size;

  editButton_.hidden = !newEntity_;
  disclosureButton_.hidden = newEntity_;
  
  ribbonedContainerView_.layer.shadowOpacity = 0.1;
  ribbonedContainerView_.layer.shadowOffset = CGSizeMake(0, 1);
  ribbonedContainerView_.layer.shadowRadius = 2;
  ribbonedContainerView_.layer.shadowPath =
      [UIBezierPath bezierPathWithRect:ribbonedContainerView_.bounds].CGPath;
  
  ribbonGradientLayer_ = [[CAGradientLayer alloc] init];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:currentUser.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (currentUser.secondaryColor) {
    [Util splitHexString:currentUser.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  ribbonGradientLayer_.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.9].CGColor,
                                (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.9].CGColor,
                                nil];
  ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;
  ribbonGradientLayer_.startPoint = CGPointMake(0.0, 0.0);
  ribbonGradientLayer_.endPoint = CGPointMake(1.0, 1.0);
  [ribbonedContainerView_.layer insertSublayer:ribbonGradientLayer_ atIndex:0];
  [ribbonGradientLayer_ release];
  
  UIView* accessoryView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  accessoryView.backgroundColor = [UIColor clearColor];
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.frame = CGRectMake(0, 1, 320, 43);
  backgroundGradient.colors = [NSArray arrayWithObjects:
      (id)[UIColor colorWithWhite:0.15 alpha:0.95].CGColor,
      (id)[UIColor colorWithWhite:0.30 alpha:0.95].CGColor, nil];
  [accessoryView.layer addSublayer:backgroundGradient];
  [backgroundGradient release];

  bottomToolbar_.layer.shadowPath = [UIBezierPath bezierPathWithRect:bottomToolbar_.bounds].CGPath;
  bottomToolbar_.layer.shadowOpacity = 0.2;
  bottomToolbar_.layer.shadowOffset = CGSizeMake(0, -1);
  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.frame = bottomToolbar_.bounds;
  toolbarGradient.colors = [NSArray arrayWithObjects:
      (id)[UIColor whiteColor].CGColor,
      (id)[UIColor colorWithWhite:0.85 alpha:1.0].CGColor, nil];
  [bottomToolbar_.layer addSublayer:toolbarGradient];
  [toolbarGradient release];

  UIButton* doneButton = [UIButton buttonWithType:UIButtonTypeCustom];
  doneButton.frame = CGRectMake(248, 4, 69, 38);
  [doneButton setImage:[UIImage imageNamed:@"done_button"] forState:UIControlStateNormal];
  doneButton.contentMode = UIViewContentModeScaleAspectFit;
  [doneButton addTarget:self
                 action:@selector(editorDoneButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [accessoryView addSubview:doneButton];
  
  UIButton* cameraButton = [UIButton buttonWithType:UIButtonTypeCustom];
  cameraButton.frame = CGRectMake(4, 4, 69, 38);
  cameraButton.contentMode = UIViewContentModeScaleAspectFit;
  [cameraButton setImage:[UIImage imageNamed:@"take_photo_button"] forState:UIControlStateNormal];
  [cameraButton setImage:[UIImage imageNamed:@"pressed_photo_button"] forState:UIControlStateHighlighted];
  [cameraButton setImage:[UIImage imageNamed:@"pressed_photo_button"] forState:UIControlStateSelected];
  [cameraButton setImage:[UIImage imageNamed:@"pressed_photo_button"] forState:UIControlStateDisabled];
  
  [cameraButton addTarget:self 
                   action:@selector(editorCameraButtonPressed:)
         forControlEvents:UIControlEventTouchDown];
  [accessoryView addSubview:cameraButton];
  self.takePhotoButton = cameraButton;

  self.reasoningTextView.inputAccessoryView = accessoryView;
  [accessoryView release];

  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36];
  titleLabel_.textColor = [UIColor stampedDarkGrayColor];

  stampLayer_ = [[CALayer alloc] init];
  stampLayer_.contents = (id)[AccountManager sharedManager].currentUser.stampImage.CGImage;
  stampLayer_.opacity = 0.0;
  [scrollView_.layer insertSublayer:stampLayer_ above:titleLabel_.layer];
  [stampLayer_ release];

  detailLabel_.textColor = [UIColor stampedGrayColor];
  // Place the reasoning label (fake placeholder) within the TextView.
  reasoningLabel_.textColor = [UIColor stampedGrayColor];
  CGRect reasoningFrame = reasoningLabel_.frame;
  reasoningFrame.origin.x = 8;
  reasoningLabel_.frame = reasoningFrame;
  [reasoningTextView_ addSubview:reasoningLabel_];

  if (creditedUser_)
    creditTextField_.text = creditedUser_.screenName;

  [self addStampsRemainingLayer];
  [self restoreViewState];
  // Twitter shit.
  GTMOAuthAuthentication* auth =
  [[[GTMOAuthAuthentication alloc] initWithSignatureMethod:kGTMOAuthSignatureMethodHMAC_SHA1
                                               consumerKey:kTwitterConsumerKey
                                                privateKey:kTwitterConsumerSecret] autorelease];
  auth.callback = kOAuthCallbackURL;
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    self.twitterAuth = auth;
    tweetButton_.enabled = YES;
  }
  if (self.fbClient.isSessionValid) {
    fbButton_.enabled = YES;
  }

  editingMask_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 460)];
  editingMask_.backgroundColor = [UIColor whiteColor];
  editingMask_.alpha = 0;
  [self.view addSubview:editingMask_];
  [editingMask_ release];
  
  creditPickerController_.creditTextField = creditTextField_;
}

- (void)addStampsRemainingLayer {
  stampsRemainingLayer_ = [[CATextLayer alloc] init];
  stampsRemainingLayer_.alignmentMode = kCAAlignmentCenter;
  stampsRemainingLayer_.frame = CGRectMake(0, 
                                           CGRectGetMaxY(self.view.frame) - 19,
                                           CGRectGetWidth(self.view.frame),
                                           CGRectGetHeight(self.view.frame));
  stampsRemainingLayer_.fontSize = 12;
  stampsRemainingLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
  stampsRemainingLayer_.contentsScale = [[UIScreen mainScreen] scale];
  stampsRemainingLayer_.shadowColor = [UIColor whiteColor].CGColor;
  stampsRemainingLayer_.shadowOpacity = 1.0;
  stampsRemainingLayer_.shadowOffset = CGSizeMake(0, 1);
  stampsRemainingLayer_.shadowRadius = 0;
  
  // TODO(andybons): this is returning nil in some cases.
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
                         (id)[UIColor stampedGrayColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName
                 value:(id)font 
                 range:[full rangeOfString:stampsLeft]];
  CFRelease(font);
  CFRelease(style);
  stampsRemainingLayer_.string = string;
  [string release];
  [self.view.layer addSublayer:stampsRemainingLayer_];
  [stampsRemainingLayer_ release];
}

- (void)restoreViewState {
  if (reasoningText_)
    reasoningTextView_.text = reasoningText_;

  if (creditedUserText_)
    creditTextField_.text = creditedUserText_;
  
  if (self.stampPhoto) {
    [self addStampPhotoView];
    [self.reasoningTextView becomeFirstResponder];
  }
}

- (void)viewDidUnload {
  self.reasoningText = reasoningTextView_.text;
  self.creditedUserText = [creditPickerController_.usersSeparatedByCommas stringByReplacingOccurrencesOfString:@"," withString:@" "];
  [[NSNotificationCenter defaultCenter] removeObserver:self]; 
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [twitterClient_.requestQueue cancelRequestsWithDelegate:self];
  if ([fbClient_.sessionDelegate isEqual:self])
    fbClient_.sessionDelegate = nil;
  self.twitterAuth = nil;
  self.twitterClient = nil;
  self.scrollView = nil;
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.bottomToolbar = nil;
  self.spinner = nil;
  self.stampItButton = nil;
  self.creditTextField.delegate = nil;
  self.creditTextField = nil;
  self.editButton = nil;
  self.mainCommentContainer = nil;
  self.backgroundImageView = nil;
  self.takePhotoButton = nil;
  self.deletePhotoButton = nil;
  self.disclosureButton = nil;
  stampsRemainingLayer_ = nil;
  self.fbClient = nil;
  self.fbButton = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  titleLabel_.text = [objectToStamp_ valueForKey:@"title"];
  detailLabel_.text = [objectToStamp_ valueForKey:@"subtitle"];
  categoryImageView_.image = [objectToStamp_ valueForKey:@"categoryImage"];
  CGSize stringSize = [titleLabel_.text sizeWithFont:titleLabel_.font
                                            forWidth:CGRectGetWidth(titleLabel_.frame)
                                       lineBreakMode:titleLabel_.lineBreakMode];
  stampLayer_.transform = CATransform3DIdentity;
  stampLayer_.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                 11 - (46 / 2),
                                 46, 46);
  stampLayer_.transform = CATransform3DMakeScale(15.0, 15.0, 1.0);
  
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;

  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.fbClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.fbClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  [super viewWillAppear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITextViewDelegate Methods.

- (void)textViewDidBeginEditing:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;
  
  self.firstResponder = reasoningTextView_;
  [self textViewDidChange:reasoningTextView_];
  reasoningTextView_.inputView = nil;
  [reasoningTextView_ reloadInputViews];
  takePhotoButton_.selected = NO;
  mainCommentContainer_.frame = [ribbonedContainerView_ convertRect:mainCommentContainer_.frame
                                                             toView:self.view];
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  [UIView animateWithDuration:0.2 
                        delay:0 
                      options:0
                   animations:^{
                     [self.view addSubview:mainCommentContainer_];
                     mainCommentContainer_.frame =
                         CGRectMake(0, 0, 320, 246 - CGRectGetHeight(reasoningTextView_.inputAccessoryView.frame));
                     deletePhotoButton_.alpha = 1.0;
                     editingMask_.alpha = 1.0;
                   }
                   completion:^(BOOL finished) {
                     reasoningTextView_.scrollEnabled = YES;
                     [self adjustTextViewContentSize];
                   }];
}

- (void)textViewDidEndEditing:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;

  self.firstResponder = nil;
  [self.navigationController setNavigationBarHidden:NO animated:YES];

  CGSize contentSize = [reasoningTextView_ sizeThatFits:CGSizeMake(241, MAXFLOAT)];
  contentSize.height += CGRectGetHeight(self.stampPhotoView.bounds) + 10;
  contentSize.height = fmaxf(104, contentSize.height);

  CGRect newContainerFrame = ribbonedContainerView_.frame;
  newContainerFrame.size.height = contentSize.height + CGRectGetHeight(creditTextField_.frame) + 8.0;
  ribbonedContainerView_.frame = newContainerFrame;
  ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;

  CGSize newContentSize = CGSizeMake(CGRectGetWidth(self.view.frame),
                                     CGRectGetMaxY(newContainerFrame) + 145);
  [scrollView_ setContentSize:newContentSize];

  shareLabel_.frame = CGRectMake(shareLabel_.frame.origin.x,
                                 CGRectGetMaxY(newContainerFrame) + 22,
                                 CGRectGetWidth(shareLabel_.frame),
                                 CGRectGetHeight(shareLabel_.frame));
  tweetButton_.frame = CGRectMake(tweetButton_.frame.origin.x,
                                  CGRectGetMaxY(newContainerFrame) + 9,
                                  CGRectGetWidth(tweetButton_.frame),
                                  CGRectGetHeight(tweetButton_.frame));
  fbButton_.frame = CGRectMake(fbButton_.frame.origin.x,
                               CGRectGetMaxY(newContainerFrame) + 9,
                               CGRectGetWidth(fbButton_.frame),
                               CGRectGetHeight(fbButton_.frame));
  
  CGFloat yOffset = floorf((CGRectGetHeight(tweetButton_.frame) - 
                            CGRectGetHeight(signInFacebookActivityIndicator_.frame)) / 2);
  signInTwitterActivityIndicator_.frame = CGRectMake(signInTwitterActivityIndicator_.frame.origin.x,
                                                     CGRectGetMinY(tweetButton_.frame) + yOffset,
                                                     CGRectGetWidth(signInTwitterActivityIndicator_.frame),
                                                     CGRectGetHeight(signInTwitterActivityIndicator_.frame));
  signInFacebookActivityIndicator_.frame = CGRectMake(signInFacebookActivityIndicator_.frame.origin.x,
                                                      CGRectGetMinY(fbButton_.frame) + yOffset,
                                                      CGRectGetWidth(signInFacebookActivityIndicator_.frame),
                                                      CGRectGetHeight(signInFacebookActivityIndicator_.frame));
  [shareLabel_ setNeedsDisplay];
  [tweetButton_ setNeedsDisplay];
  [fbButton_ setNeedsDisplay];
  [signInTwitterActivityIndicator_ setNeedsDisplay];
  [signInFacebookActivityIndicator_ setNeedsDisplay];

  CGRect newCommentFrame = CGRectMake(0, 4, 310, contentSize.height);
  CGRect convertedFrame = [self.scrollView convertRect:newCommentFrame fromView:ribbonedContainerView_];
  [UIView animateWithDuration:0.2 
                        delay:0 
                      options:UIViewAnimationOptionBeginFromCurrentState 
                   animations:^{
                     editingMask_.alpha = 0.0;
                     mainCommentContainer_.frame = convertedFrame;
                     deletePhotoButton_.alpha = 0.0;
                   } completion:^(BOOL finished) {
                     mainCommentContainer_.frame = newCommentFrame;
                     [ribbonedContainerView_ addSubview:mainCommentContainer_];
                     reasoningTextView_.contentOffset = CGPointZero;
                   }];
}

- (void)textViewDidChange:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;

  reasoningLabel_.hidden = reasoningTextView_.hasText;
  [self adjustTextViewContentSize];
}

- (void)adjustTextViewContentSize {
  if (!stampPhotoView_)
    return;

  CGSize textSize = [reasoningTextView_ sizeThatFits:reasoningTextView_.contentSize];
  CGRect picFrame = stampPhotoView_.frame;
  picFrame.origin.y = fmaxf(35, textSize.height + 1);
  CGSize contentSize = reasoningTextView_.contentSize;
  contentSize.height = CGRectGetMaxY(picFrame) - 20;
  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction
                   animations:^{
    stampPhotoView_.frame = picFrame;
    deletePhotoButton_.frame = CGRectMake(CGRectGetMaxX(stampPhotoView_.frame) - 18,
                                          CGRectGetMinY(stampPhotoView_.frame) - 12,
                                          31, 31);
    reasoningTextView_.contentSize = contentSize;
  } completion:nil];
}

#pragma mark - STCreditTextFieldDelegate Methods.

- (void)creditTextFieldDidBeginEditing:(STCreditTextField*)textField {
  if (textField != creditTextField_)
    return;
  
  self.firstResponder = creditTextField_;
  creditTextField_.frame = [ribbonedContainerView_ convertRect:creditTextField_.frame
                                                        toView:self.view];
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  [UIView animateWithDuration:0.3
                        delay:0 
                      options:0
                   animations:^{
                     [self.view addSubview:creditTextField_];
                     creditTextField_.frame = CGRectMake(0, 0, 320, CGRectGetHeight(creditTextField_.frame));
                     creditTextField_.layer.shadowOpacity = 1.0;
                     editingMask_.alpha = 1.0;
                   }
                   completion:^(BOOL finished) {}];

}

- (void)creditTextFieldDidEndEditing:(STCreditTextField*)textField {
  if (textField != creditTextField_)
    return;
  
  self.firstResponder = nil;
  [self.navigationController setNavigationBarHidden:NO animated:YES];

  CGSize contentSize = [reasoningTextView_ sizeThatFits:CGSizeMake(241, MAXFLOAT)];
  contentSize.height += CGRectGetHeight(self.stampPhotoView.bounds) + 10;
  contentSize.height = fmaxf(104, contentSize.height);
  
  CGRect newContainerFrame = ribbonedContainerView_.frame;
  newContainerFrame.size.height = contentSize.height + CGRectGetHeight(creditTextField_.frame) + 9.0;
  ribbonedContainerView_.frame = newContainerFrame;
  ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;
  
  CGSize newContentSize = CGSizeMake(CGRectGetWidth(self.view.frame),
                                     CGRectGetMaxY(newContainerFrame) + 145);
  [scrollView_ setContentSize:newContentSize];
  
  shareLabel_.frame = CGRectMake(shareLabel_.frame.origin.x,
                                 CGRectGetMaxY(newContainerFrame) + 22,
                                 CGRectGetWidth(shareLabel_.frame),
                                 CGRectGetHeight(shareLabel_.frame));
  tweetButton_.frame = CGRectMake(tweetButton_.frame.origin.x,
                                  CGRectGetMaxY(newContainerFrame) + 9,
                                  CGRectGetWidth(tweetButton_.frame),
                                  CGRectGetHeight(tweetButton_.frame));
  fbButton_.frame = CGRectMake(fbButton_.frame.origin.x,
                                  CGRectGetMaxY(newContainerFrame) + 9,
                                  CGRectGetWidth(fbButton_.frame),
                                  CGRectGetHeight(fbButton_.frame));
  
  CGFloat yOffset = floorf((CGRectGetHeight(tweetButton_.frame) - 
                            CGRectGetHeight(signInFacebookActivityIndicator_.frame)) / 2);
  signInTwitterActivityIndicator_.frame = CGRectMake(signInTwitterActivityIndicator_.frame.origin.x,
                                                     CGRectGetMinY(tweetButton_.frame) + yOffset,
                                                     CGRectGetWidth(signInTwitterActivityIndicator_.frame),
                                                     CGRectGetHeight(signInTwitterActivityIndicator_.frame));
  signInFacebookActivityIndicator_.frame = CGRectMake(signInFacebookActivityIndicator_.frame.origin.x,
                                                      CGRectGetMinY(fbButton_.frame) + yOffset,
                                                      CGRectGetWidth(signInFacebookActivityIndicator_.frame),
                                                      CGRectGetHeight(signInFacebookActivityIndicator_.frame));
  [tweetButton_ setNeedsDisplay];
  [fbButton_ setNeedsDisplay];
  [signInTwitterActivityIndicator_ setNeedsDisplay];
  [signInFacebookActivityIndicator_ setNeedsDisplay];
  [shareLabel_ setNeedsDisplay];

  CGRect frame =
      CGRectMake(0,
                 CGRectGetHeight(ribbonedContainerView_.frame) - CGRectGetHeight(creditTextField_.frame) - 5,
                 310,
                 CGRectGetHeight(creditTextField_.frame));
  CGRect convertedFrame = [self.scrollView convertRect:frame fromView:ribbonedContainerView_];
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     creditTextField_.frame = convertedFrame;
                     creditTextField_.layer.shadowOpacity = 0.0;
                     editingMask_.alpha = 0.0;
                   }
                   completion:^(BOOL finished) {
                     creditTextField_.frame = frame;
                     [ribbonedContainerView_ addSubview:creditTextField_];
                   }];
}

- (BOOL)creditTextFieldShouldReturn:(STCreditTextField*)textField {
  if (textField != creditTextField_)
    return YES;
  
  [textField resignFirstResponder];
  return NO;
}

#pragma mark - Actions.

- (IBAction)disclosureButtonPressed:(id)sender {
  UIViewController* vc = nil;
  if (entityObject_) {
    vc = [Util detailViewControllerForEntity:entityObject_];
  } else {
    vc = [Util detailViewControllerForSearchResult:(SearchResult*)objectToStamp_];
  }
  [self.navigationController pushViewController:vc animated:YES];
}

- (IBAction)tweetButtonPressed:(id)sender {
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    tweetButton_.selected = NO;
    return;
  }  
  GTMOAuthAuthentication* auth = [self createAuthentication];
  if (tweetButton_.selected == NO &&
      ![GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken authentication:auth]) {
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Stamped isn't connected to Twitter."
                                                        delegate:self
                                               cancelButtonTitle:@"Cancel"
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Connect…", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:self.view];
    return;
  }
  tweetButton_.selected = !tweetButton_.selected;
}

- (IBAction)fbButtonPressed:(id)sender {
  if (fbButton_.selected == NO && !self.fbClient.isSessionValid) {
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Stamped isn't connected to Facebook."
                                                        delegate:self
                                               cancelButtonTitle:@"Cancel"
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Connect…", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:self.view];
    return;
  }
  fbButton_.selected = !fbButton_.selected;
}

- (IBAction)editButtonPressed:(id)sender {
  EditEntityViewController* editViewController =
      [[EditEntityViewController alloc] initWithDetailedEntity:detailedEntity_];
  [self.navigationController presentModalViewController:editViewController animated:YES];
  [editViewController release];
}

- (IBAction)saveStampButtonPressed:(id)sender {
  if (savePhoto_ && self.stampPhoto)
    UIImageWriteToSavedPhotosAlbum(self.stampPhoto, nil, nil, nil);
  
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    [[Alerts alertWithTemplate:AlertTemplateNoInternet] show];
    return;
  }
  
  stampItButton_.hidden = YES;
  [spinner_ startAnimating];
  [stampItButton_ setNeedsDisplay];
  [spinner_ setNeedsDisplay];

  if (detailedEntity_ && !detailedEntity_.entityID) {
    [self sendSaveEntityRequest];
  } else {
    [self sendSaveStampRequest];
  }
}

- (void)editorDoneButtonPressed:(id)sender {
  [reasoningTextView_ resignFirstResponder];
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsZero;
  }];
  [scrollView_ setContentOffset:CGPointZero animated:YES];
}

- (void)editorCameraButtonPressed:(id)sender {
  UIButton* cameraButton = (UIButton*)sender;
  if (cameraButton.selected) {
    cameraButton.selected = NO;
    reasoningTextView_.inputView = nil;
    [reasoningTextView_ reloadInputViews];
    return;
  }

  cameraButton.selected = YES;
  
  UIView* cameraInputView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 216)];
  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  gradientLayer.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.28 alpha:1.0].CGColor,
                                (id)[UIColor colorWithWhite:0.16 alpha:1.0].CGColor, nil];
  gradientLayer.frame = cameraInputView.bounds;
  gradientLayer.startPoint = CGPointMake(0.0, 0.0);
  gradientLayer.endPoint = CGPointMake(0.0, 1.0);
  [cameraInputView.layer addSublayer:gradientLayer];
  [gradientLayer release];
  CALayer* topBorderLayer = [[CALayer alloc] init];
  topBorderLayer.backgroundColor = [UIColor blackColor].CGColor;
  topBorderLayer.frame = CGRectMake(0, 0, 320, 1);
  [cameraInputView.layer addSublayer:topBorderLayer];
  [topBorderLayer release];
  
  UIButton* takePhotoButton = [UIButton buttonWithType:UIButtonTypeCustom];
  takePhotoButton.contentMode = UIViewContentModeScaleAspectFit;
  takePhotoButton.frame = CGRectMake(3, 10, 315, 97);
  [takePhotoButton setImage:[UIImage imageNamed:@"take_photo_button_large"]
                   forState:UIControlStateNormal];
  [takePhotoButton addTarget:self
                      action:@selector(takePhotoButtonPressed:)
            forControlEvents:UIControlEventTouchUpInside];
  [cameraInputView addSubview:takePhotoButton];

  UIButton* choosePhotoButton = [UIButton buttonWithType:UIButtonTypeCustom];
  choosePhotoButton.contentMode = UIViewContentModeScaleAspectFit;
  choosePhotoButton.frame = CGRectMake(3, 109, 315, 97);
  [choosePhotoButton setImage:[UIImage imageNamed:@"choose_photo_button_large"]
                     forState:UIControlStateNormal];
  [choosePhotoButton addTarget:self
                        action:@selector(choosePhotoButtonPressed:)
              forControlEvents:UIControlEventTouchUpInside];
  [cameraInputView addSubview:choosePhotoButton];
  
  reasoningTextView_.inputView = cameraInputView;
  [cameraInputView release];
  [reasoningTextView_ reloadInputViews];
}

- (void)takePhotoButtonPressed:(id)sender {
  savePhoto_ = YES;
  UIImagePickerController* imagePicker = [[UIImagePickerController alloc] init];
  imagePicker.modalTransitionStyle = UIModalTransitionStyleCrossDissolve;
  imagePicker.sourceType = UIImagePickerControllerSourceTypeCamera;
  imagePicker.delegate = self;
  imagePicker.mediaTypes = [NSArray arrayWithObject:(NSString*)kUTTypeImage];
  [self.navigationController presentModalViewController:imagePicker animated:YES];
  [imagePicker release];
}

- (void)choosePhotoButtonPressed:(id)sender {
  savePhoto_ = NO;
  UIImagePickerController* imagePicker = [[UIImagePickerController alloc] init];
  imagePicker.modalTransitionStyle = UIModalTransitionStyleCrossDissolve;
  imagePicker.delegate = self;
  imagePicker.mediaTypes = [NSArray arrayWithObject:(NSString*)kUTTypeImage];
  [self.navigationController presentModalViewController:imagePicker animated:YES];
  [imagePicker release];
}

- (void)deletePhotoButtonPressed:(id)sender {
  if (sender != deletePhotoButton_)
    return;

  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Remove the photo?"
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:@"Remove"
                                             otherButtonTitles:nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if ([actionSheet.title rangeOfString:@"photo"].location != NSNotFound) {
    if (buttonIndex == 0) {  // Remove the photo.
      [stampPhotoView_ removeFromSuperview];
      stampPhotoView_ = nil;
      self.stampPhoto = nil;
      [deletePhotoButton_ removeFromSuperview];
      self.deletePhotoButton = nil;
      savePhoto_ = NO;
      takePhotoButton_.enabled = YES;
      takePhotoButton_.selected = NO;
      [self adjustTextViewContentSize];
      return;
    }
  }
  if ([actionSheet.title rangeOfString:@"Twitter"].location != NSNotFound) {
    if (buttonIndex == 0) {
      [self signInToTwitter];
      return;
    }
  }
  if ([actionSheet.title rangeOfString:@"Facebook"].location != NSNotFound) {
    if (buttonIndex == 0) {
      [self signInToFacebook];
      return;
    }
  }
}

#pragma mark - Network request methods.

- (void)sendSaveStampRequest {
  NSMutableDictionary* paramsDictionary = [NSMutableDictionary dictionary];
  [paramsDictionary setValue:reasoningTextView_.text forKey:@"blurb"];
  NSString* credit = creditPickerController_.usersSeparatedByCommas;
  if (credit)
    [paramsDictionary setValue:credit forKey:@"credit"];

  if ([objectToStamp_ valueForKey:@"entityID"]) {
    [paramsDictionary setValue:[objectToStamp_ valueForKey:@"entityID"] forKey:@"entity_id"];
  } else if ([objectToStamp_ valueForKey:@"searchID"]) {
    [paramsDictionary setValue:[objectToStamp_ valueForKey:@"searchID"] forKey:@"search_id"];
  }
  RKParams* params = [RKParams paramsWithDictionary:paramsDictionary];

  if (self.stampPhoto) {
    NSData* imageData = UIImageJPEGRepresentation(self.stampPhoto, 0.8);
    [params setData:imageData MIMEType:@"image/jpeg" forParam:@"image"];
  }

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateStampPath delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = params;
  [objectLoader send];
}

- (void)sendSaveEntityRequest {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* entityMapping = [objectManager.mappingProvider mappingForKeyPath:@"DetailedEntity"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateEntityPath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = entityMapping;
  
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
      detailedEntity_.title, @"title",
      detailedEntity_.subtitle, @"subtitle",
      detailedEntity_.category, @"category",
      detailedEntity_.subcategory, @"subcategory",
      nil];
  if (detailedEntity_.desc)
    [params setObject:detailedEntity_.desc forKey:@"desc"];
  if (detailedEntity_.address.length > 0)
    [params setObject:detailedEntity_.address forKey:@"address"];
  if (entityObject_.coordinates)
    [params setObject:detailedEntity_.coordinates forKey:@"coordinates"];
  objectLoader.params = params;
  [objectLoader send];
}

- (void)sendTweetRequest:(Stamp*)stamp {
  if (self.twitterAuth && tweetButton_.selected) {
    RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterUpdateStatusPath
                                                            delegate:nil];
    request.method = RKRequestMethodPOST;
    [request.URLRequest setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"];
    [request.URLRequest setHTTPMethod:@"POST"];

    NSString* blurb = [NSString stringWithFormat:@"%@. \u201c%@\u201d", stamp.entityObject.title, stamp.blurb];
    if (stamp.blurb.length == 0)
      blurb = [stamp.entityObject.title stringByAppendingString:@"."];

    NSString* substring = [blurb substringToIndex:MIN(blurb.length, 104)];
    if (blurb.length > substring.length)
      blurb = [substring stringByAppendingString:@"..."];

    // Stamped: [blurb] [link]
    NSString* tweet = [NSString stringWithFormat:@"Stamped: %@ %@", blurb, stamp.URL];
    tweet = [tweet stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
    tweet = [tweet stringByReplacingOccurrencesOfString:@"&" withString:@"%26"];  // FUCK YOU.
    NSString* body = [NSString stringWithFormat:@"status=%@", tweet];
    [request.URLRequest setHTTPBody:[body dataUsingEncoding:NSUTF8StringEncoding]];
    [self.twitterAuth authorizeRequest:request.URLRequest];
    [request send];
  }
}


- (void)signInToFacebook {
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.fbClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.fbClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  if (!self.fbClient.isSessionValid) {
    self.fbClient.sessionDelegate = self;
    [self.fbClient authorize:[[NSArray alloc] initWithObjects:@"offline_access", @"publish_stream", nil]];
  }
}

- (void)fbDidLogin {
  self.fbButton.selected = YES;
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  self.fbClient.sessionDelegate = [SharedRequestDelegate sharedDelegate];
  [[SharedRequestDelegate sharedDelegate] fbDidLogin];
}

- (void)sendFBRequest:(Stamp*)stamp {
  NSString* fbID = [[NSUserDefaults standardUserDefaults] objectForKey:@"FBID"];
  if (!fbID) {
    self.fbButton.selected = NO;
    return;
  }

  if (self.fbClient.isSessionValid && fbButton_.selected) {
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   kFacebookAppID, @"app_id",
                                   stamp.URL, @"link",
                                   stamp.entityObject.title, @"name", nil];
    NSString* photoURL = [NSString stringWithFormat:@"%@%@-%@%@", kStampLogoURLPath, stamp.user.primaryColor, stamp.user.secondaryColor, @"-logo-195x195.png"];
    [params setObject:photoURL forKey:@"picture"];

    if (stamp.blurb.length > 0)
      [params setObject:[NSString stringWithFormat:@"\"%@\"", stamp.blurb] forKey:@"message"];
    
    [self.fbClient requestWithGraphPath:[fbID stringByAppendingString:@"/feed"]
                              andParams:params
                          andHttpMethod:@"POST"
                            andDelegate:nil];
  }
}

- (void)dismissSelf {
  [twitterClient_.requestQueue cancelRequestsWithDelegate:self];
  if ([fbClient_.sessionDelegate isEqual:self])
    fbClient_.sessionDelegate = nil;
  
  
  if ([AccountManager sharedManager].currentUser.numStamps.integerValue == 1) {
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"firstStamp"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }
  StampedAppDelegate* delegate = (StampedAppDelegate*)[UIApplication sharedApplication].delegate;
  UIViewController* vc = delegate.navigationController;
  if (vc && vc.modalViewController) {
    [vc dismissModalViewControllerAnimated:YES];
  } else {
    [self.navigationController popToRootViewControllerAnimated:YES];
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  if ([objectLoader.resourcePath isEqualToString:kCreateEntityPath]) {
    DetailedEntity* entity = object;
    [objectToStamp_ setEntityID:entity.entityID];
    [self sendSaveStampRequest];
  } else if ([objectLoader.resourcePath isEqualToString:kCreateStampPath]) {
    Stamp* stamp = [Stamp objectWithPredicate:[NSPredicate predicateWithFormat:@"stampID == %@", [object valueForKey:@"stampID"]]];
    if (tweetButton_.selected)
      [self sendTweetRequest:stamp];
    if (fbButton_.selected)
      [self sendFBRequest:stamp];

    stamp.temporary = [NSNumber numberWithBool:NO];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampWasCreatedNotification
                                                        object:stamp];

    stamp.entityObject.favorite.complete = [NSNumber numberWithBool:YES];
    stamp.user.numStamps = [NSNumber numberWithInteger:(stamp.user.numStamps.integerValue + 1)];

    [stamp.managedObjectContext save:NULL];
    NSUInteger numStampsLeft = [[AccountManager sharedManager].currentUser.numStampsLeft unsignedIntegerValue];
    [AccountManager sharedManager].currentUser.numStampsLeft = [NSNumber numberWithUnsignedInteger:--numStampsLeft];

    [spinner_ stopAnimating];
    CGAffineTransform topTransform = CGAffineTransformMakeTranslation(0, -CGRectGetHeight(self.shelfView.frame));
    CGAffineTransform bottomTransform = CGAffineTransformMakeTranslation(0, CGRectGetHeight(bottomToolbar_.frame));
    [UIView animateWithDuration:0.2
                     animations:^{ 
                       self.shelfView.transform = topTransform;
                       bottomToolbar_.transform = bottomTransform;
                       stampItButton_.transform = bottomTransform;
                       stampsRemainingLayer_.transform = CATransform3DMakeAffineTransform(bottomTransform);
                     }
                     completion:^(BOOL finished) {
                       [UIView animateWithDuration:0.3
                                             delay:0
                                           options:UIViewAnimationCurveEaseIn
                                        animations:^{
                                          stampLayer_.transform = CATransform3DIdentity;
                                          stampLayer_.opacity = 1.0;
                                        }
                                        completion:^(BOOL finished) {
                                          [self performSelector:@selector(dismissSelf)
                                                     withObject:nil
                                                     afterDelay:0.75];
                                        }];
                     }];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];
  if ([objectLoader.resourcePath rangeOfString:kCreateStampPath].location != NSNotFound ||
      [objectLoader.resourcePath rangeOfString:kCreateEntityPath].location != NSNotFound) {
    if (objectLoader.response.statusCode == 403)
      [[Alerts alertWithTemplate:AlertTemplateAlreadyStamped] show];
    else 
      [[Alerts alertWithTemplate:AlertTemplateDefault] show];
  }

  [spinner_ stopAnimating];
  stampItButton_.hidden = NO;
  [UIView animateWithDuration:0.2
                   animations:^{
                     self.shelfView.transform = CGAffineTransformIdentity;
                   }];
	NSLog(@"Hit error: %@", error);
}

- (void)addStampPhotoView {
  if (!self.stampPhoto)
    return;

  stampPhotoView_ = [[UIImageView alloc] initWithImage:self.stampPhoto];
  stampPhotoView_.contentMode = UIViewContentModeScaleAspectFit;
  stampPhotoView_.layer.shadowOffset = CGSizeZero;
  stampPhotoView_.layer.shadowOpacity = 0.25;
  stampPhotoView_.layer.shadowRadius = 1.0;
  
  CGFloat width = stampPhoto_.size.width;
  CGFloat height = stampPhoto_.size.height;
  
  stampPhotoView_.frame = CGRectMake(8, 30, 200, 200 * (height / width));
  stampPhotoView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:stampPhotoView_.bounds].CGPath;
  [reasoningTextView_ addSubview:stampPhotoView_];
  [stampPhotoView_ release];
  self.deletePhotoButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [deletePhotoButton_ setImage:[UIImage imageNamed:@"delete_circle"] forState:UIControlStateNormal];
  deletePhotoButton_.frame = CGRectMake(CGRectGetMaxX(stampPhotoView_.frame) - 18,
                                        CGRectGetMinY(stampPhotoView_.frame) - 12,
                                        31, 31);

  // TODO(andybons): This doesn't appear to be working when a memory warning is called.
  [self adjustTextViewContentSize];

  [deletePhotoButton_ addTarget:self
                         action:@selector(deletePhotoButtonPressed:)
               forControlEvents:UIControlEventTouchUpInside];
  deletePhotoButton_.alpha = [reasoningTextView_ isFirstResponder] ? 1.0 : 0.0;
  [reasoningTextView_ addSubview:deletePhotoButton_];
  takePhotoButton_.enabled = NO;
}

#pragma mark - Twitter methods.

- (GTMOAuthAuthentication*)createAuthentication {
  NSString* myConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
  NSString* myConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";
  
  if ([myConsumerKey length] == 0 || [myConsumerSecret length] == 0) {
    return nil;
  }
  
  GTMOAuthAuthentication* auth;
  auth = [[[GTMOAuthAuthentication alloc] initWithSignatureMethod:kGTMOAuthSignatureMethodHMAC_SHA1
                                                      consumerKey:myConsumerKey
                                                       privateKey:myConsumerSecret] autorelease];
  [auth setServiceProvider:@"Twitter"];
  [auth setCallback:kOAuthCallbackURL];
  return auth;
}

- (void)signInToTwitter {
  GTMOAuthAuthentication *auth = [self createAuthentication];
  if (auth == nil) {
    NSAssert(NO, @"A valid consumer key and consumer secret are required for signing in to Twitter");
  }
  
  STOAuthViewController* authVC =
  [[STOAuthViewController alloc] initWithScope:kTwitterScope
                                      language:nil
                               requestTokenURL:[NSURL URLWithString:kTwitterRequestTokenURL]
                             authorizeTokenURL:[NSURL URLWithString:kTwitterAuthorizeURL]
                                accessTokenURL:[NSURL URLWithString:kTwitterAccessTokenURL]
                                authentication:auth
                                appServiceName:kKeychainTwitterToken
                                      delegate:self
                              finishedSelector:@selector(viewController:finishedWithAuth:error:)];
  [authVC setBrowserCookiesURL:[NSURL URLWithString:@"http://api.twitter.com/"]];
  
  [self.navigationController pushViewController:authVC animated:YES];
  [authVC release];
}

- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error {  
  if (error) {
    NSLog(@"GTMOAuth error = %@", error);
    return;
  }
  self.twitterAuth = auth;
  self.tweetButton.selected = YES;
  [self fetchCurrentUser];
}

- (void)fetchCurrentUser {
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:[SharedRequestDelegate sharedDelegate]];
  request.cachePolicy = RKRequestCachePolicyNone;
  [request prepareURLRequest];
  [self.twitterAuth authorizeRequest:request.URLRequest];
  [request send];
}



#pragma mark - UIImagePickerControllerDelegate methods.

- (void)imagePickerController:(UIImagePickerController*)picker didFinishPickingMediaWithInfo:(NSDictionary*)info {
  NSString* mediaType = [info objectForKey:UIImagePickerControllerMediaType];

  UIImage* original = nil;
  if (CFStringCompare((CFStringRef)mediaType, kUTTypeImage, 0) == kCFCompareEqualTo)
    original = (UIImage*)[info objectForKey:UIImagePickerControllerOriginalImage];

  if (!original)
    return;

  CGFloat width = original.size.width;
  CGFloat height = original.size.height;

  CGFloat ratio = 1.0;
  if (width > 480 || height > 480) {
    CGFloat horizontalRatio = 480 / width;
    CGFloat verticalRatio = 480 / height;
    ratio = MIN(horizontalRatio, verticalRatio);
  }
  CGRect drawRect = CGRectIntegral(CGRectMake(0, 0, width * ratio, height * ratio));
  UIGraphicsBeginImageContextWithOptions(drawRect.size, YES, 0.0);
  [original drawInRect:CGRectIntegral(CGRectMake(0, 0, drawRect.size.width, drawRect.size.height))];
  self.stampPhoto = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();

  [self addStampPhotoView];

  [self.navigationController dismissModalViewControllerAnimated:YES];
}


@end
