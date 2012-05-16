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

static NSString* const _titleFontKey = @"CreateStamp.titleFont";
static NSString* const _subtitleFontKey = @"CreateStamp.subtitleFont";
static NSString* const _addButtonFontKey = @"CreateStamp.addButtonFont";
static NSString* const _blurbFontKey = @"CreateStamp.blurbFont";

@interface STCreateStampViewController () <UITextViewDelegate, UINavigationControllerDelegate, UIImagePickerControllerDelegate>

- (void)editorCameraButtonPressed:(id)button;
- (void)editorDoneButtonPressed:(id)button;

@property (nonatomic, readonly, retain) id<STEntity> entity;
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
@property (nonatomic, readwrite, retain) UIView* bottomBar;
@property (nonatomic, readwrite, assign) CGRect bodyFrameNormal;
@property (nonatomic, readwrite, assign) CGRect bodyFrameEditing;
@property (nonatomic, readwrite, assign) CGPoint profileImageOriginHidden;
@property (nonatomic, readwrite, assign) CGPoint profileImageOriginShown;
@property (nonatomic, readwrite, assign) BOOL hasBlurbText;

@end

@implementation STCreateStampViewController

@synthesize entity = entity_;
@synthesize headerView = headerView_;
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
@synthesize bottomBar = bottomBar_;
@synthesize bodyFrameNormal = bodyFrameNormal_;
@synthesize bodyFrameEditing = bodyFrameEditing_;
@synthesize profileImageOriginHidden = profileImageOriginHidden_;
@synthesize profileImageOriginShown = profileImageOriginShown_;
@synthesize hasBlurbText = hasBlurbText_;

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

/*
 - (UIView *)loadToolbar {
 STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
 CGRect buttonFrame = CGRectMake(0, 0, 95, 41);
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
 
 UILabel* label = [Util viewWithText:@"Stamp it"
 font:[UIFont stampedBoldFontWithSize:14]
 color:[UIColor whiteColor]
 mode:UILineBreakModeClip
 andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
 label.frame = [Util centeredAndBounded:label.frame.size inFrame:buttonFrame];
 [view addSubview:label];
 
 views[i] = view;
 }
 STButton* button = [[[STButton alloc] initWithFrame:buttonFrame normalView:views[0] activeView:views[1] target:self andAction:@selector(stampButtonPressed:)] autorelease];
 button.frame = [Util centeredAndBounded:button.frame.size inFrame:toolbar.frame];
 [toolbar addSubview:button];
 return toolbar;
 }
 
 - (void)unloadToolbar {
 [self.toolbar release];
 }
 
 */

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
  self.blurbTextView = [[[UITextView alloc] initWithFrame:CGRectMake(71, 16, 215, [Util lineHeightForFont:blurbFont]*2)] autorelease];
  self.blurbTextView.font = blurbFont;
  self.blurbTextView.textColor = [UIColor stampedGrayColor];
  self.blurbTextView.delegate = self;
  self.blurbTextView.autocorrectionType = UITextAutocorrectionTypeYes;
  self.blurbTextView.keyboardAppearance = UIKeyboardAppearanceAlert;
  self.blurbTextView.scrollEnabled = NO;
  
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
  
  self.blurbImageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"TEMP_noImage"]] autorelease];
  [Util reframeView:self.blurbImageView withDeltas:CGRectMake(71, _minPhotoOffset, 0, 0)];
  self.blurbImageView.hidden = YES;
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
  self.blurbView.scrollEnabled = YES;
  [self addHiddenBlurbViews];
  [self addBlurbButtons];
  [self.bodyView addSubview:self.blurbView];
}

- (void)repositionBottomBar {
  CGRect frame = self.bottomBar.frame;
  frame.origin.y = self.bodyView.frame.size.height - (frame.size.height + 2);
  self.bottomBar.frame = frame;
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
  [self.bodyView addSubview:self.bottomBar];
  [self repositionBottomBar];
  [self loadBlurbView];
  [self.scrollView addSubview:self.bodyView];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  [self loadHeaderView];
  [self loadStampItButton];
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
  if (!self.hasBlurbText) {
    self.blurbTextView.text = @"Add a comment";
  }
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
  self.scrollView.scrollEnabled = NO;
  [UIView animateWithDuration:.40 animations:^{
    self.bodyView.frame = self.bodyFrameEditing;
    [Util reframeView:self.blurbView withDeltas:CGRectMake(5, 0, 0, 0)];
    [self repositionBottomBar];
    self.addCommentButton.hidden = YES;
    self.addPhotoButton.hidden = YES;
    self.blurbTextView.hidden = NO;
    if (!self.hasBlurbText) {
      self.blurbTextView.selectedRange = NSMakeRange(0, 0);
    }
  } completion:^(BOOL finished) {
    [UIView animateWithDuration:.25 animations:^{
      CGRect profileImageFrame = self.blurbProfileImage.frame;
      profileImageFrame.origin = self.profileImageOriginShown;
      self.blurbProfileImage.frame = profileImageFrame;
    }];
  }];
}

- (void)textViewDidEndEditing:(UITextView *)textView {
  if (self.hasBlurbText) {
    self.hasBlurbText = textView.text.length > 0;
  }
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
  self.scrollView.scrollEnabled = YES;
  [UIView animateWithDuration:.45 animations:^{
    self.bodyView.frame = self.bodyFrameNormal;
    [Util reframeView:self.blurbView withDeltas:CGRectMake(-5, 0, 0, 0)];
    [self repositionBottomBar];
    if (!self.hasBlurbText) {
      CGRect profileImageFrame = self.blurbProfileImage.frame;
      profileImageFrame.origin = self.profileImageOriginHidden;
      self.blurbProfileImage.frame = profileImageFrame;
      self.addCommentButton.hidden = NO;
      self.blurbTextView.hidden = YES;
    }
    self.addPhotoButton.hidden = NO;
    self.blurbView.contentOffset = CGPointMake(0, 0);
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

- (void)textViewDidChange:(UITextView *)textView {
  CGFloat heightDelta = textView.contentSize.height - textView.frame.size.height;
  if (heightDelta != 0) {
    [UIView animateWithDuration:.25 animations:^{
      [Util reframeView:self.blurbTextView withDeltas:CGRectMake(0, 0, 0, heightDelta)];
      CGRect photoRect = self.blurbImageView.frame;
      photoRect.origin.y = MAX( CGRectGetMaxY(self.blurbTextView.frame) + 10, _minPhotoOffset);
      self.blurbImageView.frame = photoRect;
      CGSize contentSize = self.blurbView.contentSize;
      contentSize.height = CGRectGetMaxY(self.blurbImageView.frame) + 10;
      self.blurbView.contentSize = contentSize;
      if (textView.text.length > 1) {
        NSRange selected = textView.selectedRange;
        NSString* text = [textView.text substringWithRange:NSMakeRange(0, selected.location)];
        CGSize textSize = [text sizeWithFont:textView.font constrainedToSize:textView.contentSize];
        CGFloat yOffset = MAX(0, textSize.height - 50);
        self.blurbView.contentOffset = CGPointMake(0, yOffset);
        //[Util reframeView:self.commentTextView withDeltas:CGRectMake(0, 0, 0, heightDelta)];
      }
    }];
  }
}

- (void)editorCameraButtonPressed:(id)button {
  [Util warnWithMessage:@"Add photo not implemented" andBlock:nil];
}

- (void)editorDoneButtonPressed:(id)button {
  [self.blurbTextView endEditing:YES];
}

- (void)addCommentButtonClicked:(id)notImportant {
  self.blurbTextView.hidden = NO;
  [self.blurbTextView becomeFirstResponder];
}

- (void)addPhotoButtonClicked:(id)notImportant {
  UIImagePickerController* controller = [[[UIImagePickerController alloc] init] autorelease];
  controller.delegate = self;
  controller.sourceType = UIImagePickerControllerSourceTypeCamera;
  controller.showsCameraControls = YES;
  [[Util sharedNavigationController] presentModalViewController:controller animated:YES];
}

+ (void)setupConfigurations {
  [STConfiguration addFont:[UIFont stampedTitleFontWithSize:28] forKey:_titleFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:12] forKey:_subtitleFontKey];
  [STConfiguration addFont:[UIFont stampedBoldFontWithSize:16] forKey:_addButtonFontKey];
  [STConfiguration addFont:[UIFont stampedFontWithSize:12] forKey:_blurbFontKey];
}

@end
