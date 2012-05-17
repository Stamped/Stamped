//
//  STCreateStampViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCreateStampViewController.h"
#import "STToolbarView.h"
#import "STStampDetailHeaderView.h"
#import "STRippleBar.h"
#import "AccountManager.h"
#import "STSimpleUser.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "STButton.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STStampedAPI.h"
#import "STPostStampViewController.h"
#import "STLegacyInboxViewController.h"
#import "STConfiguration.h"
#import "UIButton+Stamped.h"
#import <MobileCoreServices/UTCoreTypes.h>
#import <RestKit/NSData+MD5.h>
#import <QuartzCore/QuartzCore.h>

#import "ASIS3ObjectRequest.h"

// Amazon S3 Shit. -bons
static NSString* const kS3SecretAccessKey = @"4hqp3tVDt9ALgEFhDTqC4Y1P661uFNjtYqPVu2MW";
static NSString* const kS3AccessKeyID = @"AKIAIRLTXI62SD3BWAHQ";
static NSString* const kS3Bucket = @"stamped.com.static.temp";

static NSString* const _titleFontKey = @"CreateStamp.titleFont";
static NSString* const _subtitleFontKey = @"CreateStamp.subtitleFont";
static NSString* const _addButtonFontKey = @"CreateStamp.addButtonFont";
static NSString* const _blurbFontKey = @"CreateStamp.blurbFont";

@interface STCreateStampViewController () <UITextViewDelegate, UINavigationControllerDelegate, UIImagePickerControllerDelegate, ASIHTTPRequestDelegate>

- (void)editorCameraButtonPressed:(id)button;
- (void)editorDoneButtonPressed:(id)button;
- (void)handleImage:(UIImage*)image;
- (void)repositionImage;

@property (nonatomic, readonly, retain) id<STEntity> entity;
@property (nonatomic, readwrite, retain) UIView* blurbFadeView;
@property (nonatomic, readwrite, retain) UIView* headerView;
@property (nonatomic, readwrite, retain) UILabel* titleView;
@property (nonatomic, readwrite, retain) UILabel* subtitleView;
@property (nonatomic, readwrite, retain) UIImageView* categoryView;
@property (nonatomic, readwrite, retain) UIView* bodyView;
@property (nonatomic, readwrite, retain) UIScrollView* blurbView;
@property (nonatomic, readwrite, retain) UIView* blurbProfileImage;
@property (nonatomic, readwrite, retain) UITextView* blurbTextView;
@property (nonatomic, readwrite, retain) STButton* addCommentButton;
@property (nonatomic, readwrite, retain) STButton* addPhotoButton;
@property (nonatomic, readwrite, retain) UIImageView* blurbImageView;
@property (nonatomic, readwrite, retain) UIButton* shareTwitterButton;
@property (nonatomic, readwrite, retain) UIButton* shareFacebookButton;
@property (nonatomic, readwrite, retain) STButton* stampButton;
@property (nonatomic, readwrite, retain) STButton* deletePhotoButton;
@property (nonatomic, readwrite, retain) STButton* creditView;
@property (nonatomic, readwrite, retain) UIView* bottomBar;
@property (nonatomic, readwrite, assign) CGRect bodyFrameNormal;
@property (nonatomic, readwrite, assign) CGRect bodyFrameEditing;
@property (nonatomic, readwrite, assign) CGPoint profileImageOriginHidden;
@property (nonatomic, readwrite, assign) CGPoint profileImageOriginShown;
@property (nonatomic, readwrite, assign) BOOL hasBlurbText;
@property (nonatomic, readwrite, assign) BOOL isEditing;
@property (nonatomic, readwrite, assign) BOOL hasPhoto;

@property (nonatomic, readwrite, retain) ASIS3ObjectRequest* photoUploadRequest;
@property (nonatomic, readwrite, copy) NSString* tempPhotoURL;
@property (nonatomic, readwrite, assign) BOOL waitingForPhotoUpload;

@end

@implementation STCreateStampViewController

@synthesize entity = entity_;
@synthesize headerView = headerView_;
@synthesize blurbFadeView = blurbFadeView_;
@synthesize titleView = titleView_;
@synthesize subtitleView = subtitleView_;
@synthesize categoryView = categoryView_;
@synthesize bodyView = bodyView_;
@synthesize blurbView = blurbView_;
@synthesize blurbProfileImage = blurbProfileImage_;
@synthesize blurbTextView = blurbTextView_;
@synthesize addCommentButton = addCommentButton_;
@synthesize addPhotoButton = addPhotoButton_;
@synthesize blurbImageView = blurbImageView_;
@synthesize shareTwitterButton = shareTwitterButton_;
@synthesize shareFacebookButton = shareFacebookButton_;
@synthesize stampButton = stampButton_;
@synthesize deletePhotoButton = deletePhotoButton_;
@synthesize creditView = creditView_;
@synthesize bottomBar = bottomBar_;
@synthesize bodyFrameNormal = bodyFrameNormal_;
@synthesize bodyFrameEditing = bodyFrameEditing_;
@synthesize profileImageOriginHidden = profileImageOriginHidden_;
@synthesize profileImageOriginShown = profileImageOriginShown_;
@synthesize hasBlurbText = hasBlurbText_;
@synthesize isEditing = isEditing_;
@synthesize hasPhoto = hasPhoto_;
@synthesize photoUploadRequest = photoUploadRequest_;
@synthesize tempPhotoURL = tempPhotoURL_;
@synthesize waitingForPhotoUpload = waitingForPhotoUpload_;

static const CGFloat _yOffset = 3;
static const CGFloat _minPhotoOffset = 75;
static const CGFloat _minPhotoButtonOffset = 100;
static const CGFloat _maxPhotoButtonOffset = 135;

- (id)initWithEntity:(id<STEntity>)entity
{
  self = [super init];
  if (self) {
    entity_ = [entity retain];
  }
  return self;
}

- (void)stampButtonPressed:(id)button {
  STStampNew* stampNew = [[[STStampNew alloc] init] autorelease];
  stampNew.blurb = self.blurbTextView.text;
  stampNew.entityID = self.entity.entityID;
  [[STStampedAPI sharedInstance] createStampWithStampNew:stampNew andCallback:^(id<STStamp> stamp, NSError *error) {
    if (stamp) {
      STPostStampViewController* controller = [[[STPostStampViewController alloc] initWithStamp:stamp] autorelease];
      UIViewController* inbox = [[[[STConfiguration value:@"Root.inbox"] alloc] init] autorelease];
      [[Util sharedNavigationController] setViewControllers:[NSArray arrayWithObjects:inbox, controller, nil]
                                                   animated:YES];
    }
    else {
      [Util warnWithMessage:[NSString stringWithFormat:@"Create Stamp failed!\n%@", error] andBlock:^{
        [[Util sharedNavigationController] popViewControllerAnimated:YES];
      }];
    }
  }];
}

- (void)loadHeaderView {
  self.headerView = [[[UIView alloc] initWithFrame:CGRectMake(0, _yOffset, self.scrollView.frame.size.width, 60)] autorelease];
  self.headerView.backgroundColor = [UIColor clearColor];
  CGPoint titleOrigin = CGPointMake(15, 11);
  self.titleView = [Util viewWithText:self.entity.title 
                                 font:[STConfiguration value:_titleFontKey]
                                color:[UIColor stampedBlackColor]
                                 mode:UILineBreakModeTailTruncation
                           andMaxSize:CGSizeMake(self.scrollView.frame.size.width - titleOrigin.x * 2, CGFLOAT_MAX)];
  [Util reframeView:self.titleView withDeltas:CGRectMake(titleOrigin.x, titleOrigin.y, 0, 0)];
  [self.headerView addSubview:self.titleView];
  
  self.subtitleView = [Util viewWithText:self.entity.subtitle
                                    font:[STConfiguration value:_subtitleFontKey]
                                   color:[UIColor stampedGrayColor]
                                    mode:UILineBreakModeTailTruncation
                              andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:self.subtitleView withDeltas:CGRectMake(29, 40, 0, 0)];
  [self.headerView addSubview:self.subtitleView];
  
  self.categoryView = [[[UIImageView alloc] initWithImage:[Util imageForCategory:self.entity.category]] autorelease];
  [Util reframeView:self.categoryView withDeltas:CGRectMake(14, 40, 0, 0)];
  [self.headerView addSubview:self.categoryView];
  
  [self.scrollView addSubview:self.headerView];
}

- (void)loadStampItButton {
  CGRect buttonFrame = CGRectMake(0, 0, 90, 40);
  UIView* views[2];
  for (NSInteger i = 0; i < 2; i++) {
    UIView* view = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
    view.layer.cornerRadius = 5;
    view.layer.shadowOffset = CGSizeMake(0, 1);
    view.layer.shadowRadius = 1;
    view.layer.shadowOpacity = 1;
    NSArray* colors;
    if (i == 0) {
      // Normal view
      colors = [NSArray arrayWithObjects:
                [UIColor colorWithRed:.1 green:.4 blue:.9 alpha:1],
                [UIColor colorWithRed:.05 green:.3 blue:.7 alpha:1],
                nil];
      view.layer.shadowColor = [UIColor colorWithWhite:.85 alpha:1].CGColor;
    }
    else {
      // Active view
      colors = [NSArray arrayWithObjects:
                [UIColor colorWithRed:.05 green:.2 blue:.75 alpha:1],
                [UIColor colorWithRed:.02 green:.1 blue:.5 alpha:1],
                nil];
      view.layer.shadowColor = [UIColor colorWithWhite:.6 alpha:1].CGColor;
      
    }
    [Util addGradientToLayer:view.layer withColors:colors vertical:YES];
    
    UILabel* label = [Util viewWithText:@"Stamp it!"
                                   font:[UIFont stampedBoldFontWithSize:14]
                                  color:[UIColor whiteColor]
                                   mode:UILineBreakModeClip
                             andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    label.frame = [Util centeredAndBounded:label.frame.size inFrame:buttonFrame];
    [view addSubview:label];
    
    views[i] = view;
  }
  self.stampButton = [[[STButton alloc] initWithFrame:buttonFrame normalView:views[0] activeView:views[1] target:self andAction:@selector(stampButtonPressed:)] autorelease];
  [Util reframeView:self.stampButton withDeltas:CGRectMake(225, 356 + _yOffset, 0, 0)];
  [self.scrollView addSubview:self.stampButton];
}

- (void)addBlurbTextView {
  
  UIFont* blurbFont = [STConfiguration value:_blurbFontKey];
  self.blurbTextView = [[[UITextView alloc] initWithFrame:CGRectMake(71, 16, 215, 40)] autorelease];
  self.blurbTextView.font = blurbFont;
  self.blurbTextView.textColor = [UIColor stampedGrayColor];
  self.blurbTextView.delegate = self;
  self.blurbTextView.autocorrectionType = UITextAutocorrectionTypeYes;
  self.blurbTextView.keyboardAppearance = UIKeyboardAppearanceAlert;
  self.blurbTextView.scrollEnabled = NO;
  self.blurbTextView.clipsToBounds = NO;
  
  UIView* accessoryView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)] autorelease];
  accessoryView.backgroundColor = [UIColor clearColor];
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.frame = CGRectMake(0, 1, 320, 43);
  backgroundGradient.colors = [NSArray arrayWithObjects:
                               (id)[UIColor colorWithWhite:0.15 alpha:0.95].CGColor,
                               (id)[UIColor colorWithWhite:0.30 alpha:0.95].CGColor, nil];
  [accessoryView.layer addSublayer:backgroundGradient];
  [backgroundGradient release];
  
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
  self.blurbTextView.inputAccessoryView = accessoryView;
  self.blurbTextView.hidden = YES;
  
  [self.blurbView addSubview:self.blurbTextView];
}

- (void)addHiddenBlurbViews {
  self.blurbProfileImage = [Util profileImageViewForUser:[STStampedAPI sharedInstance].currentUser withSize:STProfileImageSize46];
  self.profileImageOriginHidden = CGPointMake(-10 - self.blurbProfileImage.frame.size.width, 15);
  self.profileImageOriginShown = CGPointMake(20, 15);
  [Util reframeView:self.blurbProfileImage withDeltas:CGRectMake(self.profileImageOriginHidden.x, self.profileImageOriginHidden.y, 0, 0)];
  [self.blurbView addSubview:self.blurbProfileImage];
  
  [self addBlurbTextView];
  
  self.blurbImageView = [[[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 1, 1)] autorelease];
  [Util reframeView:self.blurbImageView withDeltas:CGRectMake(71, _minPhotoOffset, 0, 0)];
  self.blurbImageView.hidden = YES;
  self.deletePhotoButton = [STButton buttonWithNormalImage:[UIImage imageNamed:@"delete_comment_icon"]
                                               activeImage:[UIImage imageNamed:@"delete_comment_icon"]
                                                    target:self 
                                                 andAction:@selector(deletePhotoButtonClicked:)];
  [self.blurbImageView addSubview:self.deletePhotoButton];
  [self.blurbView addSubview:self.blurbImageView];
}

- (void)addBlurbButtons {
  CGFloat addCommentWidth = 200;
  CGFloat addPhotoWidth = 80;
  CGRect addCommentButtonFrame = CGRectMake((self.blurbView.frame.size.width - addCommentWidth) / 2, 54, 200, 40);
  CGRect addPhotoButtonFrame = CGRectMake((self.blurbView.frame.size.width - addPhotoWidth) / 2, _minPhotoButtonOffset, 80, 40);
  
  NSString* messages[] = {
    @"Add a Comment",
    @"Add a Photo",
  };
  for (NSInteger i = 0; i < 2; i++) {
    UIView* views[2];
    for (NSInteger k = 0; k < 2; k++) {
      CGSize buttonSize;
      if (i == 0) {
        buttonSize = addCommentButtonFrame.size;
      }
      else {
        buttonSize = addPhotoButtonFrame.size;
      }
      UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, buttonSize.width, buttonSize.height)] autorelease];
      view.layer.cornerRadius = buttonSize.height / 2;
      UIColor* borderColor;
      view.layer.borderWidth = 1;
      if (k == 0) {
        view.backgroundColor = [UIColor whiteColor];
        borderColor = [UIColor colorWithWhite:229/255.0 alpha:1];
      }
      else {
        view.backgroundColor = [UIColor colorWithWhite:.85 alpha:1];
        borderColor = [UIColor colorWithWhite:198/255.0 alpha:1];
      }
      view.layer.borderColor = borderColor.CGColor;
      views[k] = view;
    }
    CGPoint origin;
    SEL selector;
    if (i == 0) {
      origin = addCommentButtonFrame.origin;
      selector = @selector(addCommentButtonClicked:);
    }
    else {
      origin = addPhotoButtonFrame.origin;
      selector = @selector(addPhotoButtonClicked:);
    }
    STButton* button = [[[STButton alloc] initWithFrame:views[0].frame
                                             normalView:views[0]
                                             activeView:views[1]
                                                 target:self
                                              andAction:selector] autorelease];
    if (i == 0) {
      UILabel* text = [Util viewWithText:messages[i]
                                    font:[STConfiguration value:_addButtonFontKey]
                                   color:[UIColor stampedDarkGrayColor]
                                    mode:UILineBreakModeTailTruncation
                              andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
      text.frame = [Util centeredAndBounded:text.frame.size inFrame:button.frame];
      [button addSubview:text];
    }
    else {
      UIImageView* image = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"photo_icon"]] autorelease];
      image.frame = [Util centeredAndBounded:image.frame.size inFrame:button.frame];
      [button addSubview:image];
    }
    [Util reframeView:button withDeltas:CGRectMake(origin.x, origin.y, 0, 0)];
    if (i == 0) {
      self.addCommentButton = button;
    }
    else {
      self.addPhotoButton = button;
    }
    [self.blurbView addSubview:button];
  }
  //self.addPhotoButton.inputView = [[[UIView alloc] initWithFrame:CGRectMake(10, 0, 200, 50)] autorelease];
  self.addPhotoButton.inputView.backgroundColor = [UIColor redColor];
}

- (void)loadBlurbView {
  self.blurbView = [[[UIScrollView alloc] initWithFrame:CGRectMake(-5, 6, self.scrollView.frame.size.width, 196)] autorelease];
  self.blurbView.backgroundColor = [UIColor whiteColor];
  self.blurbView.scrollEnabled = NO;
  self.blurbView.clipsToBounds = NO;
  [self addHiddenBlurbViews];
  self.blurbFadeView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.blurbView.frame.size.width, self.blurbView.frame.size.height)] autorelease];
  
  CGFloat fadeOffset = 90;
  CGFloat fadeHeight = 35;
  UIView* fade = [[[UIView alloc] initWithFrame:CGRectMake(0, fadeOffset, self.blurbFadeView.frame.size.width, fadeHeight)] autorelease];
  [Util addGradientToLayer:fade.layer 
                withColors:[NSArray arrayWithObjects:[UIColor colorWithWhite:1 alpha:0], [UIColor colorWithWhite:1 alpha:1], nil]
                  vertical:YES];
  [self.blurbFadeView addSubview:fade];
  UIView* opaque = [[[UIView alloc] initWithFrame:CGRectMake(0,
                                                             CGRectGetMaxY(fade.frame),
                                                             self.blurbFadeView.frame.size.width,
                                                             400)] autorelease];
  opaque.backgroundColor = [UIColor whiteColor];
  [self.blurbFadeView addSubview:opaque];
  self.blurbFadeView.userInteractionEnabled = NO;
  [self.blurbView addSubview:self.blurbFadeView];
  [self addBlurbButtons];
  [self.bodyView addSubview:self.blurbView];
}

- (void)repositionBottomBar {
  CGRect frame = self.bottomBar.frame;
  frame.origin.y = self.bodyView.frame.size.height - (frame.size.height + 2);
  self.bottomBar.frame = frame;
}

- (void)repositionCreditView {
  CGRect frame = self.creditView.frame;
  frame.origin.y = self.bodyView.frame.size.height - 60;
  self.creditView.frame = frame;
}

- (void)creditViewClicked:(id)notImportant {
  [Util warnWithMessage:@"Too be implemented between 5/23 and 5/25" andBlock:nil];
}

- (void)loadCreditView {
  CGRect creditFrame = CGRectMake(0, 0, self.scrollView.frame.size.width, 60);
  UIView* views[2];
  for (NSInteger i = 0; i < 2; i++) {
    UIView* view = [[[UIView alloc] initWithFrame:creditFrame] autorelease];
    if (i == 0) {
      view.backgroundColor = [UIColor whiteColor];
    }
    else {
      [Util addGradientToLayer:view.layer 
                    withColors:[NSArray arrayWithObjects:
                                [UIColor whiteColor],
                                [UIColor stampedLightGrayColor],
                                [UIColor whiteColor],
                                nil]
                      vertical:YES];
    }
    views[i] = view;
  }
  self.creditView = [[[STButton alloc] initWithFrame:creditFrame 
                                          normalView:views[0] 
                                          activeView:views[1]
                                              target:self 
                                           andAction:@selector(creditViewClicked:)] autorelease];
  self.creditView.layer.shadowRadius = 2;
  self.creditView.layer.shadowOffset = CGSizeMake(0, -2);
  self.creditView.layer.shadowColor = [UIColor blackColor].CGColor;
  self.creditView.layer.shadowOpacity = .2;
  self.creditView.backgroundColor = [UIColor whiteColor];
  
  UIImageView* creditIcon = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_icon"]] autorelease];
  [Util reframeView:creditIcon withDeltas:CGRectMake(10, 16, 25 - creditIcon.frame.size.width, 16 - creditIcon.frame.size.height)];
  [self.creditView addSubview:creditIcon];
  
  UIView* creditText = [Util viewWithText:@"Who deserves credit?"
                                     font:[UIFont stampedFontWithSize:12]
                                    color:[UIColor stampedGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:creditText withDeltas:CGRectMake(41, 20, 0, 0)];
  [self.creditView addSubview:creditText];
  
  [self repositionCreditView];
  [self.bodyView addSubview:self.creditView];
}

- (void)loadBodyView {
  self.bodyFrameNormal = CGRectMake(5, 60 + _yOffset, 310, 256);
  self.bodyFrameEditing = CGRectMake(0, -6, self.scrollView.frame.size.width, [Util standardFrameWithNavigationBar:NO].size.height);
  self.bodyView = [[[UIView alloc] initWithFrame:self.bodyFrameNormal] autorelease];
  self.bodyView.backgroundColor = [UIColor whiteColor];
  self.bodyView.clipsToBounds = YES;
  id<STUser> user = [STStampedAPI sharedInstance].currentUser;
  UIView* topBar = [[[STRippleBar alloc] initWithFrame:CGRectMake(0, 0, 320, 3.5)
                                       andPrimaryColor:user.primaryColor 
                                     andSecondaryColor:user.secondaryColor 
                                                 isTop:YES] autorelease];
  [Util reframeView:topBar withDeltas:CGRectMake(0, 2, 0, 0)];
  [self.bodyView addSubview:topBar];
  self.bottomBar = [[[STRippleBar alloc] initWithFrame:CGRectMake(0, 0, 320, 3.5)
                                       andPrimaryColor:user.primaryColor 
                                     andSecondaryColor:user.secondaryColor 
                                                 isTop:NO] autorelease];
  [self loadBlurbView];
  [self loadCreditView];
  [self.bodyView addSubview:self.bottomBar];
  self.bottomBar.backgroundColor = [UIColor clearColor];
  [self repositionBottomBar];
  [self.scrollView addSubview:self.bodyView];
}

- (void)shareTwitterButtonClicked:(UIButton*)button {
  button.selected = !button.selected;
}

- (void)shareFacebookButtonClicked:(UIButton*)button {
  button.selected = !button.selected;
}

- (void)loadShareButtons {
  self.shareTwitterButton = [[[UIButton alloc] initWithFrame:CGRectMake(10, 356, 45, 40)] autorelease];
  [self.shareTwitterButton setImage:[UIImage imageNamed:@"share_twitter"] forState:UIControlStateNormal];
  [self.shareTwitterButton setImage:[UIImage imageNamed:@"share_twitter_on"] forState:UIControlStateSelected];
  [self.shareTwitterButton setImage:[UIImage imageNamed:@"share_twitter_highlighted"] forState:UIControlStateHighlighted];
  [self.shareTwitterButton addTarget:self action:@selector(shareTwitterButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
  [self.scrollView addSubview:self.shareTwitterButton];
  self.shareFacebookButton = [[[UIButton alloc] initWithFrame:self.shareTwitterButton.frame] autorelease];
  [Util reframeView:self.shareFacebookButton withDeltas:CGRectMake(self.shareTwitterButton.frame.size.width + 2, 0, 0, 0)];
  [self.shareFacebookButton setImage:[UIImage imageNamed:@"share_fb"] forState:UIControlStateNormal];
  [self.shareFacebookButton setImage:[UIImage imageNamed:@"share_fb_on"] forState:UIControlStateSelected];
  [self.shareFacebookButton setImage:[UIImage imageNamed:@"share_fb_highlighted"] forState:UIControlStateHighlighted];
  [self.shareFacebookButton addTarget:self action:@selector(shareFacebookButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
  [self.scrollView addSubview:self.shareFacebookButton];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  [self loadHeaderView];
  [self loadStampItButton];
  [self loadShareButtons];
  [self loadBodyView];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (BOOL)textFieldShouldBeginEditing:(UITextField *)textField {
  return self.hasBlurbText;
}

- (void)textViewDidBeginEditing:(UITextView *)textView {
  self.isEditing = YES;
  if (!self.hasBlurbText) {
    self.blurbTextView.text = @"Add a comment";
  }
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
  self.scrollView.scrollEnabled = NO;
  self.blurbView.scrollEnabled = YES;
  [UIView animateWithDuration:.40 animations:^{
    self.bodyView.frame = self.bodyFrameEditing;
    [self repositionCreditView];
    [Util reframeView:self.blurbView withDeltas:CGRectMake(5, 0, 0, 0)];
    [self repositionBottomBar];
    self.addCommentButton.hidden = YES;
    self.addPhotoButton.hidden = YES;
    self.blurbTextView.hidden = NO;
    if (!self.hasBlurbText) {
      self.blurbTextView.selectedRange = NSMakeRange(0, 0);
    }
    self.blurbFadeView.alpha = 0;
  } completion:^(BOOL finished) {
    [UIView animateWithDuration:.2 animations:^{
      CGRect profileImageFrame = self.blurbProfileImage.frame;
      profileImageFrame.origin = self.profileImageOriginShown;
      self.blurbProfileImage.frame = profileImageFrame;
    }];
  }];
}

- (void)textViewDidEndEditing:(UITextView *)textView {
  self.isEditing = NO;
  if (self.hasBlurbText) {
    self.hasBlurbText = textView.text.length > 0;
  }
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
  self.scrollView.scrollEnabled = YES;
  self.blurbView.scrollEnabled = NO;
  [UIView animateWithDuration:.45 animations:^{
    self.bodyView.frame = self.bodyFrameNormal;
    [self repositionCreditView];
    [Util reframeView:self.blurbView withDeltas:CGRectMake(-5, 0, 0, 0)];
    [self repositionBottomBar];
    if (!self.hasBlurbText) {
      CGRect profileImageFrame = self.blurbProfileImage.frame;
      profileImageFrame.origin = self.profileImageOriginHidden;
      self.blurbProfileImage.frame = profileImageFrame;
      self.addCommentButton.hidden = NO;
      self.blurbTextView.hidden = YES;
    }
    self.blurbView.contentOffset = CGPointMake(0, 0);
    [self repositionPhotoButton];
    if (!self.hasPhoto) {
      self.blurbFadeView.alpha = 1;
      self.addPhotoButton.hidden = NO;
    }
  }];
}

- (BOOL)textViewShouldEndEditing:(UITextView *)textView {
  [textView resignFirstResponder];
  return YES;
}

- (BOOL)textView:(UITextView *)textView shouldChangeTextInRange:(NSRange)range replacementText:(NSString *)text
{
  if (!self.hasBlurbText) {
    textView.text = @"";
    self.hasBlurbText = YES;
  }
  return YES;
}

- (void)textViewChange:(UITextView*)textView {
  [UIView animateWithDuration:.25 
                        delay:0 
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     CGRect blurbTextFrame = self.blurbTextView.frame;
                     blurbTextFrame.size.height = self.blurbTextView.contentSize.height;
                     self.blurbTextView.frame = blurbTextFrame;
                     [self repositionImage];
                     if (textView.text.length > 1) {
                       NSRange selected = textView.selectedRange;
                       NSString* text = [textView.text substringWithRange:NSMakeRange(0, selected.location)];
                       CGSize textSize = [text sizeWithFont:textView.font constrainedToSize:textView.contentSize];
                       CGFloat yOffset = MAX(0, textSize.height - 100);
                       self.blurbView.contentOffset = CGPointMake(0, yOffset);
                     }
                   }
                   completion:nil];
}


- (void)textViewDidChange:(UITextView *)textView {
  [self textViewChange:textView];
}

- (void)textViewDidChangeSelection:(UITextView *)textView {
  [self textViewChange:textView];
}

- (void)activateCamera:(BOOL)takePicture {
  UIImagePickerController* controller = [[[UIImagePickerController alloc] init] autorelease];
  controller.delegate = self;
  if (takePicture) {
    controller.sourceType = UIImagePickerControllerSourceTypeCamera;
    controller.showsCameraControls = YES;
  }
  [[Util sharedNavigationController] presentModalViewController:controller animated:YES];
}


- (void)editorCameraButtonPressed:(id)button {
  if ([UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypeCamera]) {
    [Util menuWithTitle:@"Choose method" 
                message:nil 
                choices:[NSArray arrayWithObjects:@"Take Picture", @"Choose Picture", nil]
               andBlock:^(NSString *string) {
                 if ([string isEqualToString:@"Take Picture"]) {
                   [self activateCamera:YES];
                 }
                 else if ([string isEqualToString:@"Choose Picture"]) {
                   [self activateCamera:NO];
                 }
               }];
  }
  else {
    //[self activateCamera:NO];
    [self handleImage:[UIImage imageNamed:@"TEMP_noImage"]];
  }
}

- (void)editorDoneButtonPressed:(id)button {
  [self.blurbTextView endEditing:YES];
}

- (void)addCommentButtonClicked:(id)notImportant {
  self.blurbTextView.hidden = NO;
  [self.blurbTextView becomeFirstResponder];
}

- (void)addPhotoButtonClicked:(id)notImportant {
  [self editorCameraButtonPressed:nil];
}

- (void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary *)info {
  [[Util sharedNavigationController] dismissModalViewControllerAnimated:YES]; 
  UIImage* image = [info objectForKey:UIImagePickerControllerEditedImage];
  if (!image) {
    image = [info objectForKey:UIImagePickerControllerOriginalImage];
  }
  if (image) {
    [self handleImage:image];
  }
};

- (void)imagePickerControllerDidCancel:(UIImagePickerController *)picker {
  [[Util sharedNavigationController] dismissModalViewControllerAnimated:YES];
}

- (void)handleImage:(UIImage*)image {
  self.hasPhoto = YES;
  self.blurbFadeView.alpha = 0;
  self.addPhotoButton.hidden = YES;
  self.blurbImageView.image = image;
  CGRect bounds = CGRectMake(self.blurbImageView.frame.origin.x, 
                             self.blurbImageView.frame.origin.y,
                             self.blurbTextView.frame.size.width, 
                             image.size.height);
  CGFloat y = self.blurbImageView.frame.origin.y;
  CGFloat x = self.blurbImageView.frame.origin.x;
  bounds = [Util centeredAndBounded:image.size inFrame:bounds];
  bounds.origin.y = y;
  bounds.origin.x = x;
  self.blurbImageView.frame = bounds;
  self.blurbImageView.hidden = NO;
  [self.blurbImageView addGestureRecognizer:[[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(deletePhotoButtonClicked:)] autorelease]];
  [self repositionCommentButton];
  [self repositionImage];
  self.blurbImageView.userInteractionEnabled = YES;
  [self uploadPhotoToS3];
}

- (void)uploadPhotoToS3 {
  if (!self.blurbImageView.image)
    return;
  [Util globalLoadingLock];
  self.waitingForPhotoUpload = YES;
  
  NSData* imageData = UIImageJPEGRepresentation(self.blurbImageView.image, 0.8);
  NSDate* now = [NSDate date];
  NSString* key = [NSString stringWithFormat:@"%@-%.0f.jpg", [imageData MD5], now.timeIntervalSince1970];
  ASIS3ObjectRequest* request = [ASIS3ObjectRequest PUTRequestForData:imageData withBucket:kS3Bucket key:key];
  request.secretAccessKey = kS3SecretAccessKey;
  request.delegate = self;
  request.accessKey = kS3AccessKeyID;
  request.accessPolicy = ASIS3AccessPolicyPublicRead;
  request.timeOutSeconds = 30;
  request.numberOfTimesToRetryOnTimeout = 2;
  request.mimeType = @"image/jpeg";
  request.shouldAttemptPersistentConnection = NO;
  [ASIS3Request setShouldUpdateNetworkActivityIndicator:NO];
  [request startAsynchronous];
  self.photoUploadRequest = request;
  self.tempPhotoURL = [NSString stringWithFormat:@"http://s3.amazonaws.com/stamped.com.static.temp/%@", key];
}

- (CGFloat)blurbTextMaxY {
  return self.blurbTextView.frame.origin.y + self.blurbTextView.contentSize.height;
}

- (void)repositionImage {
  CGRect photoRect = self.blurbImageView.frame;
  photoRect.origin.y = MAX( [self blurbTextMaxY] + 10, _minPhotoOffset);
  if (!self.blurbImageView.image) {
    photoRect.size = CGSizeMake(1, 1);
  }
  self.blurbImageView.frame = photoRect;
  
  CGSize contentSize = self.blurbView.contentSize;
  contentSize.height = CGRectGetMaxY(self.blurbImageView.frame) + 10;
  self.blurbView.contentSize = contentSize;
}

- (void)repositionCommentButton {
  CGRect frame = self.addCommentButton.frame;
  if (self.hasPhoto) {
    frame.origin.y = 20;
  }
  else {
    frame.origin.y = 54;
  }
  self.addCommentButton.frame = frame;
}

- (void)repositionPhotoButton {
  CGRect frame = self.addPhotoButton.frame;
  CGFloat y = MAX(_minPhotoButtonOffset,[self blurbTextMaxY] + 5);
  frame.origin.y = MIN(y, _maxPhotoButtonOffset);
  self.addPhotoButton.frame = frame;
  
}

- (void)deletePhotoButtonClicked:(id)notImportant {
  self.blurbImageView.image = nil;
  self.hasPhoto = NO;
  self.blurbImageView.hidden = YES;
  self.addPhotoButton.hidden = NO;
  self.tempPhotoURL = nil;
  [self updateLayout];
}

- (void)updateLayout {
  [self repositionImage];
  [self repositionCommentButton];
  [self repositionPhotoButton];
  if (!self.hasPhoto) {
    self.addPhotoButton.hidden = self.isEditing;
  }
  else {
    self.addPhotoButton.hidden = YES;
  }
}

+ (void)setupConfigurations {
  [STConfiguration addFont:[UIFont stampedTitleFontWithSize:28] forKey:_titleFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:12] forKey:_subtitleFontKey];
  [STConfiguration addFont:[UIFont stampedBoldFontWithSize:16] forKey:_addButtonFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:12] forKey:_blurbFontKey];
}


#pragma mark - ASIRequestDelegate methods.

- (void)requestFinished:(ASIHTTPRequest*)request {
  self.waitingForPhotoUpload = NO;
  self.photoUploadRequest = nil;
  [Util globalLoadingUnlock];
}

- (void)requestFailed:(ASIHTTPRequest*)request {
  self.photoUploadRequest = nil;
  self.tempPhotoURL = nil;
  self.waitingForPhotoUpload = NO;
  [Util globalLoadingUnlock];
  [Util warnWithMessage:@"Photo upload failed" andBlock:nil];
}

@end
