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

@interface STCreateStampViewController () <UITextViewDelegate>

- (void)editorCameraButtonPressed:(id)button;
- (void)editorDoneButtonPressed:(id)button;

@property (nonatomic, readonly, retain) id<STEntity> entity;
@property (nonatomic, readwrite, retain) UIView* bodyView;
@property (nonatomic, readwrite, retain) UIScrollView* blurbView;
@property (nonatomic, readwrite, retain) UIView* blurbProfileImage;
@property (nonatomic, readwrite, retain) UITextView* blurbTextView;
@property (nonatomic, readwrite, retain) UIView* addCommentButton;
@property (nonatomic, readwrite, retain) UIView* addPhotoButton;
@property (nonatomic, readwrite, retain) UIImageView* blurbImageView;
@property (nonatomic, readwrite, retain) UIButton* shareTwitterButton;
@property (nonatomic, readwrite, retain) UIButton* shareFacebookButton;
@property (nonatomic, readwrite, retain) STButton* stampButton;

@end

@implementation STCreateStampViewController

@synthesize entity = entity_;
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

- (void)loadBodyView {
  self.bodyView = [[[UIView alloc] initWithFrame:CGRectMake(5, 0, 310, 256)] autorelease];
  self.bodyView.backgroundColor = [UIColor whiteColor];
  id<STUser> user = [STStampedAPI sharedInstance].currentUser;
  UIView* topBar = [[[STRippleBar alloc] initWithPrimaryColor:user.primaryColor andSecondaryColor:user.secondaryColor isTop:YES] autorelease];
  [Util reframeView:topBar withDeltas:CGRectMake(0, 2, 0, 0)];
  [self.bodyView addSubview:topBar];
  UIView* bottomBar = [[[STRippleBar alloc] initWithPrimaryColor:user.primaryColor andSecondaryColor:user.secondaryColor isTop:NO] autorelease];
  [Util reframeView:bottomBar withDeltas:CGRectMake(0, self.bodyView.frame.size.height - (bottomBar.frame.size.height + 2), 0, 0)];
  [self.bodyView addSubview:bottomBar];
  [self.scrollView appendChildView:self.bodyView];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  UIView* view = [[[STStampDetailHeaderView alloc] initWithEntity:self.entity] autorelease];
  [self.scrollView appendChildView:view];
  
  
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
  /*
  self.textView.inputAccessoryView = accessoryView;
  [body appendChildView:self.textView];
  UIView* bottomBar = [[[STRippleBar alloc] initWithPrimaryColor:user.primaryColor andSecondaryColor:user.secondaryColor isTop:NO] autorelease];
  [body appendChildView:bottomBar];
  [self.scrollView appendChildView:body];
   */
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (void)textViewDidBeginEditing:(UITextView *)textView {
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
}

- (BOOL)textViewShouldEndEditing:(UITextView *)textView {
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
  [textView resignFirstResponder];
  return YES;
}

- (void)editorCameraButtonPressed:(id)button {
  [Util warnWithMessage:@"Add photo not implemented" andBlock:nil];
}

- (void)editorDoneButtonPressed:(id)button {
  //[self.textView endEditing:YES];
}

@end
