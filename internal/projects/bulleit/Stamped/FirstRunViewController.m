//
//  FirstRunViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import "FirstRunViewController.h"

@interface FirstRunViewController ()
- (void)setupBottomView;
- (void)setupSlide:(UIImageView*)imageView;
- (void)setSecondaryButtonsVisible:(BOOL)visible;

@property (nonatomic, assign) BOOL editing;
@end

@implementation FirstRunViewController

@synthesize scrollView = scrollView_;
@synthesize bottomView = bottomView_;
@synthesize animationContentView = animationContentView_;
@synthesize signInButton = signInButton_;
@synthesize createAccountButton = createAccountButton_;
@synthesize cancelButton = cancelButton_;
@synthesize confirmButton = confirmButton_;
@synthesize signInScrollView = signInScrollView_;
@synthesize stampedLogo = stampedLogo_;
@synthesize editing = editing_;
@synthesize usernameTextField = usernameTextField_;
@synthesize passwordTextField = passwordTextField_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  [self setupBottomView];

  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"],
                                                [UIImage imageNamed:@"learnmore_01"],
                                                [UIImage imageNamed:@"learnmore_02"],
                                                [UIImage imageNamed:@"learnmore_03"],
                                                [UIImage imageNamed:@"learnmore_04"], nil];
  
  for (NSUInteger i = 0; i < bgImages.count; ++i) {
    CGRect frame = self.scrollView.frame;
    frame.origin.x = self.scrollView.frame.size.width * i;
    
    UIImageView* subview = [[UIImageView alloc] initWithFrame:frame];
    subview.image = [bgImages objectAtIndex:i];
    subview.clipsToBounds = YES;
    subview.contentMode = UIViewContentModeRight;
    
    if (i == 1)
      [self setupSlide:subview];

    [self.scrollView addSubview:subview];
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(CGRectGetWidth(self.scrollView.frame) * bgImages.count,
                                           CGRectGetHeight(self.scrollView.frame));
  
  self.cancelButton.alpha = 0.0;
  self.confirmButton.alpha = 0.0;
  self.confirmButton.titleLabel.textAlignment = UITextAlignmentCenter;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [self.signInScrollView removeFromSuperview];

  self.bottomView = nil;
  self.scrollView = nil;
  self.animationContentView = nil;
  self.createAccountButton = nil;
  self.signInButton = nil;
  self.cancelButton = nil;
  self.confirmButton = nil;
  self.signInScrollView = nil;
  self.stampedLogo = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Setup Views

- (void)setupBottomView {
  CAGradientLayer* bottomGradient = [[CAGradientLayer alloc] init];
  bottomGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.88 alpha:1.0].CGColor, nil];
  bottomGradient.frame = bottomView_.bounds;
  
  
  [bottomView_.layer insertSublayer:bottomGradient atIndex:0];
  [bottomGradient release];
}

- (void)setupSlide:(UIImageView*)imageView {
  UIImage* starImg = [UIImage imageNamed:@"learnmore_star"];

  for (NSUInteger i = 0; i < 5; ++i) {
    UIImageView* starView = [[UIImageView alloc] initWithImage:starImg];
    CGRect frame = CGRectMake(26 + (i * starImg.size.width - 12), 95, starImg.size.width, starImg.size.height);
    starView.frame = frame;
    starView.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.5];
    [imageView addSubview:starView];
    [starView release];
  }
}


#pragma mark - Transitions

- (void)setSecondaryButtonsVisible:(BOOL)visible {
  [UIView animateWithDuration:0.2 animations:^{
    confirmButton_.alpha = visible ? 1.0 : 0.0;
    cancelButton_.alpha = visible ? 1.0 : 0.0;
    createAccountButton_.alpha = visible ? 0.0 : 1.0;
    signInButton_.alpha = visible ? 0.0 : 1.0;
  }];
}

#pragma mark - Nib Actions.

- (IBAction)createAccountButtonPressed:(id)sender {
  if (sender != createAccountButton_)
    return;
  
  confirmButton_.enabled = NO;
  [confirmButton_ setTitle:@"Join" forState:UIControlStateNormal];
  [self setSecondaryButtonsVisible:YES];
}

- (IBAction)signInButtonPressed:(id)sender {
  if (sender != signInButton_)
    return;

  if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero))
    [self.view addSubview:stampedLogo_];

  [confirmButton_ setTitle:@"Sign in" forState:UIControlStateNormal];
  confirmButton_.enabled = NO;
  [self setSecondaryButtonsVisible:YES];
  [self.view insertSubview:signInScrollView_ atIndex:0];
  [UIView animateWithDuration:0.2 animations:^{
    animationContentView_.alpha = 0.0;
  } completion:^(BOOL finished) {
    if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero))
      [signInScrollView_ addSubview:stampedLogo_];
  }];
}

- (IBAction)cancelButtonPressed:(id)sender {
  if (sender != cancelButton_)
    return;
  
  usernameTextField_.text = nil;
  passwordTextField_.text = nil;
  // This is a visual hack to prevent the logo from cross-fading if switching
  // between the login screen and the learn more flow (but only if the learn more
  // flow is at the first slide).
  if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero) && !editing_)
    [self.view addSubview:stampedLogo_];
  
  [self setSecondaryButtonsVisible:NO];
  [UIView animateWithDuration:0.2 animations:^{
    animationContentView_.alpha = 1.0;
  } completion:^(BOOL finished) {
    if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero) && !editing_)
      [signInScrollView_ addSubview:stampedLogo_];
    [signInScrollView_ removeFromSuperview];
  }];
}

- (IBAction)confirmButtonPressed:(id)sender {
  if (sender != confirmButton_)
    return;
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  editing_ = YES;
  if (textField.superview == signInScrollView_) {
    [UIView animateWithDuration:0.3
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState 
                     animations:^{
                       signInScrollView_.frame = CGRectOffset(signInScrollView_.frame, 0, -216);
                       bottomView_.frame = CGRectOffset(bottomView_.frame, 0, -216);
                     } 
                     completion:nil];
  }
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  editing_ = NO;
  if (textField.superview == signInScrollView_) {
    [UIView animateWithDuration:0.3 
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState 
                     animations:^{
                       signInScrollView_.frame = CGRectOffset(signInScrollView_.frame, 0, 216);
                       bottomView_.frame = CGRectOffset(bottomView_.frame, 0, 216);
                     } 
                     completion:nil];
  }
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];

  return YES;
}

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  if (textField.superview == signInScrollView_) {
    // enable/disable sign-in button.
  }

  return YES;
}


@end
