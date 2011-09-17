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
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "EditEntityViewController.h"
#import "Entity.h"
#import "Favorite.h"
#import "STNavigationBar.h"
#import "Notifications.h"
#import "Stamp.h"
#import "UserImageView.h"
#import "Util.h"
#import "User.h"
#import "UIColor+Stamped.h"

static NSString* const kCreateStampPath = @"/stamps/create.json";
static NSString* const kCreateEntityPath = @"/entities/create.json";

@interface STCreditTextField : UITextField
@end

@implementation STCreditTextField

- (CGRect)textRectForBounds:(CGRect)bounds {
  return CGRectOffset(CGRectInset(bounds, 37, 0), 37, 0);
}

- (CGRect)editingRectForBounds:(CGRect)bounds {    
  return CGRectOffset(CGRectInset(bounds, 37, 0), 37, 0);
}

@end

@interface CreateStampViewController ()
- (void)editorDoneButtonPressed:(id)sender;
- (void)editorCameraButtonPressed:(id)sender;
- (void)takePhotoButtonPressed:(id)sender;
- (void)choosePhotoButtonPressed:(id)sender;
- (void)deletePhotoButtonPressed:(id)sender;
- (void)adjustTextViewContentSize;
- (void)sendSaveStampRequest;
- (void)sendSaveEntityRequest;
- (void)dismissSelf;
- (void)addStampPhotoView;
- (void)restoreViewState;
- (void)addStampsRemainingLayer;

@property (nonatomic, retain) UIImage* stampPhoto;
@property (nonatomic, retain) UIButton* takePhotoButton;
@property (nonatomic, retain) UIButton* deletePhotoButton;
@property (nonatomic, retain) UIImageView* stampPhotoView;
@property (nonatomic, copy) NSString* reasoningText;
@property (nonatomic, copy) NSString* creditedUserText;
@property (nonatomic, assign) BOOL savePhoto;
@property (nonatomic, retain) UIResponder* firstResponder;
@property (nonatomic, readonly) CATextLayer* stampsRemainingLayer;
@property (nonatomic, readonly) UIImageView* tooltipImageView;
@end

@implementation CreateStampViewController

@synthesize scrollView = scrollView_;
@synthesize titleLabel = titleLabel_;
@synthesize detailLabel = detailLabel_;
@synthesize reasoningLabel = reasoningLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize userImageView = userImageView_;
@synthesize ribbonedContainerView = ribbonedContainerView_;
@synthesize reasoningTextView = reasoningTextView_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize shelfBackground = shelfBackground_;
@synthesize spinner = spinner_;
@synthesize stampItButton = stampItButton_;
@synthesize creditTextField = creditTextField_;
@synthesize editButton = editButton_;
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
@synthesize tooltipImageView = tooltipImageView_;
@synthesize creditLabel = creditLabel_;

- (id)initWithEntityObject:(Entity*)entityObject {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entityObject retain];
  }
  return self;
}

- (id)initWithEntityObject:(Entity*)entityObject creditedTo:(User*)user {
  self = [self initWithEntityObject:entityObject];
  if (self) {
    creditedUser_ = [user retain];
  }
  return self;
}

- (void)dealloc {
  [entityObject_ release];
  [creditedUser_ release];
  self.stampPhoto = nil;
  self.reasoningText = nil;
  self.creditedUserText = nil;
  self.firstResponder = nil;

  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  User* currentUser = [AccountManager sharedManager].currentUser;
  self.userImageView.imageURL = currentUser.profileImageURL;
  scrollView_.contentSize = self.view.bounds.size;

  editButton_.hidden = entityObject_.entityID != nil;
  
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
  titleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];

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
  
  NSString* stampsLeft = [[AccountManager sharedManager].currentUser.numStamps stringValue];
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
  self.creditedUserText = self.creditTextField.text;

  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.scrollView = nil;
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.bottomToolbar = nil;
  self.shelfBackground = nil;
  self.spinner = nil;
  self.stampItButton = nil;
  self.creditTextField = nil;
  self.editButton = nil;
  self.mainCommentContainer = nil;
  self.backgroundImageView = nil;
  self.takePhotoButton = nil;
  self.deletePhotoButton = nil;
  stampsRemainingLayer_ = nil;
  tooltipImageView_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  titleLabel_.text = entityObject_.title;
  detailLabel_.text = entityObject_.subtitle;
  categoryImageView_.image = entityObject_.categoryImage;
  CGSize stringSize = [titleLabel_.text sizeWithFont:titleLabel_.font
                                            forWidth:CGRectGetWidth(titleLabel_.frame)
                                       lineBreakMode:titleLabel_.lineBreakMode];
  stampLayer_.transform = CATransform3DIdentity;
  stampLayer_.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                 11 - (46 / 2),
                                 46, 46);
  stampLayer_.transform = CATransform3DMakeScale(15.0, 15.0, 1.0);

  [super viewWillAppear:animated];
}



- (void)viewDidAppear:(BOOL)animated {
  if (!tooltipImageView_) {
    tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"tooltip_taphere"]];
    tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame, (self.view.frame.size.width-tooltipImageView_.frame.size.width)/2, 140);
    tooltipImageView_.alpha = 0.0;
    [self.view addSubview:tooltipImageView_];
    [tooltipImageView_ release];
  }
  
  if (![[NSUserDefaults standardUserDefaults] valueForKey:@"hasStamped"])
      [UIView  animateWithDuration:0.3 delay:0.75 options:nil animations:^{tooltipImageView_.alpha = 1.0;} completion:nil];
  
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITextViewDelegate Methods.

- (void)textViewDidBeginEditing:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;
  
  if (![[NSUserDefaults standardUserDefaults] valueForKey:@"hasStamped"])
    [UIView animateWithDuration:0.15 animations:^{tooltipImageView_.alpha = 0.0;}];
  
  self.firstResponder = reasoningTextView_;
  [self textViewDidChange:reasoningTextView_];
  reasoningTextView_.inputView = nil;
  [reasoningTextView_ reloadInputViews];
  takePhotoButton_.selected = NO;

  mainCommentContainer_.frame = [ribbonedContainerView_ convertRect:mainCommentContainer_.frame
                                                             toView:self.view];
  [self.view addSubview:mainCommentContainer_];
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  CGRect frame = CGRectMake(0, 0, 320, 246 - CGRectGetHeight(reasoningTextView_.inputAccessoryView.frame));
  scrollView_.hidden = YES;
  backgroundImageView_.hidden = YES;
  [UIView animateWithDuration:0.2
                   animations:^{
                     mainCommentContainer_.frame = frame;
                     deletePhotoButton_.alpha = 1.0;
                   } completion:^(BOOL finished) {
                     reasoningTextView_.scrollEnabled = YES;
                     [self adjustTextViewContentSize];
                   }];
}

- (void)textViewDidEndEditing:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;

  self.firstResponder = nil;
  scrollView_.hidden = NO;
  backgroundImageView_.hidden = NO;
  [self.navigationController setNavigationBarHidden:NO animated:YES];

  CGSize contentSize = [reasoningTextView_ sizeThatFits:CGSizeMake(310, MAXFLOAT)];
  contentSize.height += CGRectGetHeight(self.stampPhotoView.bounds) + 10;
  CGRect newCommentFrame = CGRectMake(0, 4, 310, fmaxf(104, contentSize.height));
  CGRect convertedFrame = [self.view convertRect:newCommentFrame fromView:ribbonedContainerView_];  
  CGRect newContainerFrame = ribbonedContainerView_.frame;
  newContainerFrame.size.height = CGRectGetHeight(convertedFrame) + 58.0;
  CGSize newContentSize = CGSizeMake(CGRectGetWidth(self.view.frame),
                                     CGRectGetMaxY(newContainerFrame) + 65);
  [scrollView_ setContentSize:newContentSize];
  ribbonedContainerView_.frame = newContainerFrame;
  ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;

  [UIView animateWithDuration:0.2 animations:^{
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

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  if (textField != creditTextField_)
    return;
  
  if (![[NSUserDefaults standardUserDefaults] valueForKey:@"hasStamped"])
    [UIView animateWithDuration:0.15 animations:^{tooltipImageView_.alpha = 0.0;}];
  
  self.creditLabel.text = @"Credit to";
  
  self.firstResponder = creditTextField_;
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset =
      UIEdgeInsetsMake(0, 0, CGRectGetMaxY(ribbonedContainerView_.frame) - 50, 0);
    [self.scrollView setContentOffset:CGPointMake(0, CGRectGetMaxY(ribbonedContainerView_.frame) - 50) animated:YES];
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  if (textField != creditTextField_)
    return;

  if ([textField.text isEqualToString:@""])
    self.creditLabel.text = @"Who deserves credit?";
  
  self.firstResponder = nil;
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset = UIEdgeInsetsZero;
  }];
  [self.scrollView setContentOffset:CGPointZero animated:YES];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != creditTextField_)
    return YES;
  
  [textField resignFirstResponder];
  return NO;
}

#pragma mark - Actions.

- (IBAction)editButtonPressed:(id)sender {
  EditEntityViewController* editViewController =
      [[EditEntityViewController alloc] initWithEntity:entityObject_];
  [self.navigationController presentModalViewController:editViewController animated:YES];
  [editViewController release];
}

- (IBAction)backButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)saveStampButtonPressed:(id)sender {
  stampItButton_.hidden = YES;
  [spinner_ startAnimating];
  [stampItButton_ setNeedsDisplay];
  [spinner_ setNeedsDisplay];
  
  if (savePhoto_ && self.stampPhoto)
    UIImageWriteToSavedPhotosAlbum(self.stampPhoto, nil, nil, nil);

  if (entityObject_.entityID) {
    [self sendSaveStampRequest];
  } else {
    [self sendSaveEntityRequest];
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
  }
}

#pragma mark - Network request methods.

- (void)sendSaveStampRequest {
  NSString* credit = [creditTextField_.text stringByReplacingOccurrencesOfString:@" " withString:@""];
  RKParams* params = [RKParams paramsWithDictionary:[NSDictionary dictionaryWithObjectsAndKeys:
      reasoningTextView_.text, @"blurb",
      credit, @"credit",
      entityObject_.entityID, @"entity_id", nil]];

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
  RKObjectMapping* entityMapping = [objectManager.mappingProvider mappingForKeyPath:@"Entity"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateEntityPath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = entityMapping;
  
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
      entityObject_.title, @"title",
      entityObject_.subtitle, @"subtitle",
      entityObject_.category, @"category",
      entityObject_.subcategory, @"subcategory",
      nil];
  if (entityObject_.desc)
    [params setObject:entityObject_.desc forKey:@"desc"];
  if (entityObject_.address.length > 0)
    [params setObject:entityObject_.address forKey:@"address"];
  if (entityObject_.coordinates)
    [params setObject:entityObject_.coordinates forKey:@"coordinates"];
  objectLoader.params = params;
  [objectLoader send];
}

- (void)dismissSelf {
  UIViewController* vc = self.navigationController.parentViewController;
  if (vc && vc.modalViewController) {
    [vc dismissModalViewControllerAnimated:YES];
  } else {
    [self.navigationController popToRootViewControllerAnimated:YES];
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  if ([objectLoader.resourcePath isEqualToString:kCreateEntityPath]) {
    Entity* entity = object;
    entityObject_.entityID = entity.entityID;
    [entityObject_.managedObjectContext save:NULL];
    [self sendSaveStampRequest];
  } else if ([objectLoader.resourcePath isEqualToString:kCreateStampPath]) {
    Stamp* stamp = object;
    stamp.temporary = [NSNumber numberWithBool:NO];
    [entityObject_ addStampsObject:stamp];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampWasCreatedNotification
                                                        object:stamp];
    entityObject_.favorite.complete = [NSNumber numberWithBool:YES];
    entityObject_.favorite.stamp = stamp;
    [stamp.managedObjectContext save:NULL];
    [[NSNotificationCenter defaultCenter] postNotificationName:kFavoriteHasChangedNotification
                                                        object:stamp];
    NSUInteger numStamps = [[AccountManager sharedManager].currentUser.numStamps unsignedIntegerValue];
    [AccountManager sharedManager].currentUser.numStamps = [NSNumber numberWithUnsignedInteger:--numStamps];

    [spinner_ stopAnimating];
    CGAffineTransform topTransform = CGAffineTransformMakeTranslation(0, -CGRectGetHeight(shelfBackground_.frame));
    CGAffineTransform bottomTransform = CGAffineTransformMakeTranslation(0, CGRectGetHeight(bottomToolbar_.frame));
    [UIView animateWithDuration:0.2
                     animations:^{ 
                       shelfBackground_.transform = topTransform;
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

  NSLog(@"response: %@", objectLoader.response.bodyAsString);
  [spinner_ stopAnimating];
  stampItButton_.hidden = NO;
  [UIView animateWithDuration:0.2
                   animations:^{
                     shelfBackground_.transform = CGAffineTransformIdentity;
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

  if ((width > height && width > 320) || (height > width && height > 480)) {
    CGFloat horizontalRatio = 320 / width;
    CGFloat verticalRatio = 480 / height;
    CGFloat ratio = MIN(horizontalRatio, verticalRatio);
    CGRect drawRect = CGRectIntegral(CGRectMake(0, 0, width * ratio, height * ratio));
    UIGraphicsBeginImageContextWithOptions(drawRect.size, YES, 0.0);
    [original drawInRect:CGRectIntegral(CGRectMake(0, 0, drawRect.size.width, drawRect.size.height))];
    self.stampPhoto = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
  } else {
    self.stampPhoto = original;
  }

  [self addStampPhotoView];

  [self.navigationController dismissModalViewControllerAnimated:YES];
}


@end
