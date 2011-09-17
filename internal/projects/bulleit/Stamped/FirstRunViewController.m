//
//  FirstRunViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import "FirstRunViewController.h"

#import <MobileCoreServices/UTCoreTypes.h>

#import "UserImageView.h"
#import "WelcomeViewController.h"

static const CGFloat kKeyboardOffset = 216;
static const CGFloat kProfileImageSize = 500;

@interface FirstRunViewController ()
- (void)setupBottomView;
- (void)setupSlide:(UIImageView*)imageView;
- (void)setSecondaryButtonsVisible:(BOOL)visible;

@property (nonatomic, assign) BOOL editing;
@property (nonatomic, retain) UIImage* profilePhoto;
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
@synthesize signUpScrollView = signUpScrollView_;
@synthesize signUpEmailTextField = signUpEmailTextField_;
@synthesize signUpPhoneTextField = signUpPhoneTextField_;
@synthesize signUpFullNameTextField = signUpFullNameTextField_;
@synthesize signUpPasswordTextField = signUpPasswordTextField_;
@synthesize signUpUsernameTextField = signUpUsernameTextField_;
@synthesize userImageView = userImageView_;
@synthesize profilePhoto = profilePhoto_;
@synthesize activityIndicator = activityIndicator_;
@synthesize delegate = delegate_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.delegate = nil;

  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  [self setupBottomView];

  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"],
                                                [UIImage imageNamed:@"learnmore_01"],
                                                [UIImage imageNamed:@"learnmore_02"],
                                                [UIImage imageNamed:@"learnmore_03"],
                                                [UIImage imageNamed:@"learnmore_04b"], nil];
  
  for (NSUInteger i = 0; i < bgImages.count; ++i) {
    UIImageView* subview = [[UIImageView alloc] initWithImage:[bgImages objectAtIndex:i]];

    CGRect frame = self.scrollView.frame;
    frame.origin.x = CGRectGetWidth(frame) * i;
    if (i == 4) {
      UIImageView* learnMore = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"learnmore_04"]];
      learnMore.frame = frame;
      [self.scrollView addSubview:learnMore];
      [learnMore release];
    }
    subview.frame = frame;
    
    subview.clipsToBounds = YES;
    subview.contentMode = UIViewContentModeCenter;
    
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
  signUpScrollView_.contentSize = CGRectInset(signUpScrollView_.bounds, 0, 20).size;
  userImageView_.enabled = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [self.signInScrollView removeFromSuperview];
  [self.signUpScrollView removeFromSuperview];

  self.bottomView = nil;
  self.scrollView = nil;
  self.animationContentView = nil;
  self.createAccountButton = nil;
  self.signInButton = nil;
  self.cancelButton = nil;
  self.confirmButton = nil;
  self.signInScrollView = nil;
  self.stampedLogo = nil;
  self.signUpScrollView = nil;
  self.signUpEmailTextField = nil;
  self.signUpPhoneTextField = nil;
  self.signUpFullNameTextField = nil;
  self.signUpPasswordTextField = nil;
  self.signUpUsernameTextField = nil;
  self.userImageView = nil;
  self.profilePhoto = nil;
  self.activityIndicator = nil;
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

- (void)signInFailed:(NSString*)reason {
  if (signInScrollView_.superview) {
    [activityIndicator_ stopAnimating];
    [confirmButton_ setTitle:@"Sign in" forState:UIControlStateNormal];
    confirmButton_.enabled = YES;
  }
}

- (void)signUpSucess {
  WelcomeViewController* welcomeVC = [[WelcomeViewController alloc] init];
  [self.navigationController pushViewController:welcomeVC animated:YES];
  [welcomeVC release];
}

- (void)signUpFailed:(NSString*)reason {
  NSString* reasoning = @"Please check that all required fields are valid. Sorry. We're working on making this easier.";
  UIAlertView* alert = [[UIAlertView alloc] initWithTitle:@"Womp womp"
                                                  message:reasoning
                                                 delegate:nil
                                        cancelButtonTitle:@"OK"
                                        otherButtonTitles:nil];
  [alert show];
  [alert release];

  [activityIndicator_ stopAnimating];
  [confirmButton_ setTitle:@"Join" forState:UIControlStateNormal];
  confirmButton_.enabled = YES;
}

#pragma mark - Nib Actions.

- (IBAction)createAccountButtonPressed:(id)sender {
  if (sender != createAccountButton_)
    return;
  
  confirmButton_.enabled = NO;
  [confirmButton_ setTitle:@"Join" forState:UIControlStateNormal];
  [self setSecondaryButtonsVisible:YES];
  [self.view insertSubview:signUpScrollView_ atIndex:0];
  [UIView animateWithDuration:0.2 animations:^{
    animationContentView_.alpha = 0.0;
  }];
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

  // This is a visual hack to prevent the logo from cross-fading if switching
  // between the login screen and the learn more flow (but only if the learn more
  // flow is at the first slide and not editing.).
  if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero) && !editing_ && !signUpScrollView_.superview)
    [self.view addSubview:stampedLogo_];
  
  [activityIndicator_ stopAnimating];
  [self setSecondaryButtonsVisible:NO];
  [UIView animateWithDuration:0.2 animations:^{
    animationContentView_.alpha = 1.0;
  } completion:^(BOOL finished) {
    if (CGPointEqualToPoint(scrollView_.contentOffset, CGPointZero) && !editing_ && !signUpScrollView_.superview)
      [signInScrollView_ addSubview:stampedLogo_];

    [signInScrollView_ removeFromSuperview];
    [signUpScrollView_ removeFromSuperview];
    usernameTextField_.text = nil;
    passwordTextField_.text = nil;
    signUpFullNameTextField_.text = nil;
    signUpUsernameTextField_.text = nil;
    signUpEmailTextField_.text = nil;
    signUpPasswordTextField_.text = nil;
    signUpPhoneTextField_.text = nil;
    userImageView_.imageView.image = [UIImage imageNamed:@"profile_placeholder"];
  }];
}

- (IBAction)confirmButtonPressed:(id)sender {
  if (sender != confirmButton_)
    return;
  
  confirmButton_.enabled = NO;
  [confirmButton_ setTitle:nil forState:UIControlStateNormal];
  [activityIndicator_ startAnimating];
  if (signInScrollView_.superview) {
    [delegate_ viewController:self didReceiveUsername:usernameTextField_.text password:passwordTextField_.text];
  } else if (signUpScrollView_.superview) {
    NSString* num = nil;
    if (signUpPhoneTextField_.text) {
      num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet punctuationCharacterSet]] componentsJoinedByString: @""];
      num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet symbolCharacterSet]] componentsJoinedByString: @""];
      num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] componentsJoinedByString: @""];
      num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet letterCharacterSet]] componentsJoinedByString: @""];
    }
    [delegate_ viewController:self
       willCreateUserWithName:signUpFullNameTextField_.text
                     username:signUpUsernameTextField_.text
                     password:signUpPasswordTextField_.text
                        email:signUpEmailTextField_.text
                 profileImage:userImageView_.imageView.image
                  phoneNumber:num];
  }
}

- (IBAction)takePhotoButtonPressed:(id)sender {
  UIActionSheet* sheet = [[UIActionSheet alloc] initWithTitle:nil
                                                     delegate:self
                                            cancelButtonTitle:@"Cancel"
                                       destructiveButtonTitle:nil
                                            otherButtonTitles:@"Take photo", @"Choose photo", nil];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
  [sheet release];
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 2)
    return;  // Canceled.
  
  UIImagePickerController* imagePicker = [[UIImagePickerController alloc] init];
  imagePicker.modalTransitionStyle = UIModalTransitionStyleCrossDissolve;
  imagePicker.delegate = self;
  imagePicker.allowsEditing = YES;
  imagePicker.mediaTypes = [NSArray arrayWithObject:(NSString*)kUTTypeImage];

  if (buttonIndex == 0) {
    imagePicker.sourceType = UIImagePickerControllerSourceTypeCamera;
    imagePicker.cameraDevice = UIImagePickerControllerCameraDeviceFront;
  }
  [self presentModalViewController:imagePicker animated:YES];
  [imagePicker release];
}

#pragma mark - UIImagePickerControllerDelegate methods.

- (void)imagePickerController:(UIImagePickerController*)picker didFinishPickingMediaWithInfo:(NSDictionary*)info {
  NSString* mediaType = [info objectForKey:UIImagePickerControllerMediaType];

  if (CFStringCompare((CFStringRef)mediaType, kUTTypeImage, 0) == kCFCompareEqualTo) {
    UIImage* photo = (UIImage*)[info objectForKey:UIImagePickerControllerEditedImage];
  
    UIGraphicsBeginImageContext(CGSizeMake(kProfileImageSize, kProfileImageSize));
    [photo drawInRect:CGRectMake(0, 0, kProfileImageSize, kProfileImageSize)];
    self.profilePhoto = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    userImageView_.imageView.image = profilePhoto_;
  }
  [self dismissModalViewControllerAnimated:YES];
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  editing_ = YES;
  if (textField.superview == signInScrollView_) {
    [UIView animateWithDuration:0.3
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState 
                     animations:^{
                       animationContentView_.frame = CGRectOffset(animationContentView_.frame, 0, -kKeyboardOffset);
                       bottomView_.frame = CGRectOffset(bottomView_.frame, 0, -kKeyboardOffset);
                       signInScrollView_.frame = CGRectOffset(signInScrollView_.frame, 0, -kKeyboardOffset);
                     }
                     completion:nil];
  } else if (textField.superview == signUpScrollView_) {
    CGFloat offset = (kKeyboardOffset - CGRectGetHeight(bottomView_.bounds)) / 2;
    [UIView animateWithDuration:0.3
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState 
                     animations:^{
                       signUpScrollView_.frame = CGRectInset(CGRectOffset(signUpScrollView_.frame, 0, -offset), 0, offset);
                       [signUpScrollView_ scrollRectToVisible:textField.frame animated:YES];
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
                       animationContentView_.frame = CGRectOffset(animationContentView_.frame, 0, kKeyboardOffset);
                       bottomView_.frame = CGRectOffset(bottomView_.frame, 0, kKeyboardOffset);
                       signInScrollView_.frame = CGRectOffset(signInScrollView_.frame, 0, kKeyboardOffset);
                     }
                     completion:nil];
  } else if (textField.superview == signUpScrollView_) {
    CGPoint contentOffset = signUpScrollView_.contentOffset;
    CGFloat offset = (kKeyboardOffset - CGRectGetHeight(bottomView_.bounds)) / 2;
    [UIView animateWithDuration:0.3
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState 
                     animations:^{
                       signUpScrollView_.frame = CGRectInset(CGRectOffset(signUpScrollView_.frame, 0, offset), 0, -offset);
                       signUpScrollView_.contentOffset = contentOffset;
                     }
                     completion:^(BOOL finished) {
                       if (!editing_) {
                         [UIView animateWithDuration:0.2 animations:^{
                           signUpScrollView_.contentOffset = CGPointZero;
                         }];
                       }
                     }];
  }
}

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  if (textField.superview == signInScrollView_) {
    if (textField == usernameTextField_) {
      confirmButton_.enabled = passwordTextField_.text.length &&
          [textField.text stringByReplacingCharactersInRange:range withString:string].length;
    } else if (textField == passwordTextField_) {
      confirmButton_.enabled = usernameTextField_.text.length &&
          [textField.text stringByReplacingCharactersInRange:range withString:string].length;
    }
  }
  return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  UIView* nextView = [textField.superview viewWithTag:textField.tag + 1];
  if (nextView) {
    [nextView becomeFirstResponder];
  } else {
    if (textField.superview == signUpScrollView_) {
      confirmButton_.enabled = (signUpFullNameTextField_.text.length &&
                                signUpUsernameTextField_.text.length &&
                                signUpEmailTextField_.text.length &&
                                signUpPasswordTextField_.text.length);
    } else if (textField.superview == signInScrollView_) {
      confirmButton_.enabled = (usernameTextField_.text.length &&
                                passwordTextField_.text.length);
    }
    [textField resignFirstResponder];
  }
  return YES;
}


@end
