//
//  FirstRunViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import "FirstRunViewController.h"

#import <MobileCoreServices/UTCoreTypes.h>
#import "TTTAttributedLabel.h"

#import "UserImageView.h"
#import "WelcomeViewController.h"
#import "Util.h"
#import "TOSViewController.h"
#import "WebViewController.h"
#import "AccountManager.h"

static const CGFloat kKeyboardOffset = 216;
static const CGFloat kProfileImageSize = 500;
static  NSString* const kStampedTermsURL = @"http://www.stamped.com/terms-mobile.html";
static  NSString* const kStampedPrivacyURL = @"http://www.stamped.com/privacy-mobile.html";
static  NSString* const kStampedValidateURI = @"/account/check.json";

@interface FirstRunViewController ()
- (void)setupBottomView;
- (void)setSecondaryButtonsVisible:(BOOL)visible;

@property (nonatomic, assign) BOOL editing;
@property (nonatomic, retain) UIImage* profilePhoto;
@property (nonatomic, copy) NSString* fullName;
@property (nonatomic, copy) NSString* username;
@property (nonatomic, copy) NSString* email;
@property (nonatomic, copy) NSString* password;
@property (nonatomic, copy) NSString* phone;
@property (nonatomic, retain) NSTimer* timer;
@property (nonatomic, retain) RKRequestQueue* requestQueue;
@property (nonatomic, retain) UIColor* primaryColor;
@property (nonatomic, retain) UIColor* secondaryColor;
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
@synthesize validationButton = validationButton_;
@synthesize timer = timer_;
@synthesize requestQueue = requestQueue_;
@synthesize primaryColor = primaryColor_;
@synthesize secondaryColor = secondaryColor_;
@synthesize validationStampView = validationStampView_;
@synthesize validationStamp1ImageView = validationStamp1ImageView_;
@synthesize validationStamp2ImageView = validationStamp2ImageView_;
@synthesize validationCheckImageView = validationCheckImageView_;

@synthesize fullName = fullName_;
@synthesize username = username_;
@synthesize email = email_;
@synthesize password = password_;
@synthesize phone = phone_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.delegate = nil;
  self.profilePhoto = nil;
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
  self.activityIndicator = nil;
  self.validationButton = nil;
  self.timer = nil;
  if (requestQueue_)
    [requestQueue_ cancelAllRequests];
  self.requestQueue = nil;
  self.primaryColor = nil;
  self.secondaryColor = nil;
  self.validationStampView = nil;
  self.validationStamp1ImageView = nil;
  self.validationStamp2ImageView = nil;
  self.validationCheckImageView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  
  requestQueue_ = [[RKRequestQueue alloc] init];
  requestQueue_.requestTimeout = 30;
  requestQueue_.delegate = self;
  requestQueue_.concurrentRequestsLimit = 1;
  [requestQueue_ start];
  
  [self setupBottomView];
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
  self.activityIndicator = nil;
  self.validationButton = nil;
  self.timer = nil;
  [requestQueue_ cancelAllRequests];
  self.requestQueue = nil;
  self.primaryColor = nil;
  self.secondaryColor = nil;
  self.validationStampView = nil;
  self.validationStamp1ImageView = nil;
  self.validationStamp2ImageView = nil;
  self.validationCheckImageView = nil;
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
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp"
                                                   message:@"Wrong username and password combination."
                                                  delegate:nil
                                         cancelButtonTitle:@"OK"
                                         otherButtonTitles:nil] autorelease];
  [alert show];
}

- (void)signUpSucess {
  WelcomeViewController* welcomeVC = [[WelcomeViewController alloc] init];
  [self.navigationController pushViewController:welcomeVC animated:YES];
  [welcomeVC release];
}

- (void)signUpFailed:(NSString*)reason {
  [activityIndicator_ stopAnimating];
  [confirmButton_ setTitle:@"Join" forState:UIControlStateNormal];
  confirmButton_.enabled = YES;
  NSString* reasoning = @"Please check that all required fields are valid. Sorry. We're working on making this easier.";
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp"
                                                  message:reasoning
                                                 delegate:nil
                                        cancelButtonTitle:@"OK"
                                        otherButtonTitles:nil] autorelease];
  [alert show];
}

#pragma mark - Nib Actions.

- (IBAction)createAccountButtonPressed:(id)sender {
  confirmButton_.enabled = fullName_ && username_ && email_ && password_;
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
    userImageView_.imageView.image = [UIImage imageNamed:@"welcome_profile_placeholder"];
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
    NSString* num = [Util sanitizedPhoneNumberFromString:signUpPhoneTextField_.text];
    [delegate_ viewController:self
       willCreateUserWithName:signUpFullNameTextField_.text
                     username:signUpUsernameTextField_.text
                     password:signUpPasswordTextField_.text
                        email:signUpEmailTextField_.text
                 profileImage:self.profilePhoto
                  phoneNumber:num];
  }
}

- (IBAction)takePhotoButtonPressed:(id)sender {
  // Save state.
  self.fullName = signUpFullNameTextField_.text;
  self.username = signUpUsernameTextField_.text;
  self.email = signUpEmailTextField_.text;
  self.password = signUpPasswordTextField_.text;
  self.phone = signUpPhoneTextField_.text;
  UIActionSheet* sheet = [[UIActionSheet alloc] initWithTitle:nil
                                                     delegate:self
                                            cancelButtonTitle:@"Cancel"
                                       destructiveButtonTitle:nil
                                            otherButtonTitles:@"Take photo", @"Choose photo", nil];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
  [sheet release];
}

- (IBAction)termsButtonPressed:(id)sender {
  TOSViewController* vc = [[TOSViewController alloc] initWithURL:[NSURL URLWithString:kStampedTermsURL]];
  [self.navigationController presentModalViewController:vc animated:YES];
  vc.settingsButton.hidden = YES;
  [vc release];
}

- (IBAction)privacyButtonPressed:(id)sender {
  TOSViewController* vc = [[TOSViewController alloc] initWithURL:[NSURL URLWithString:kStampedPrivacyURL]];
  [self.navigationController presentModalViewController:vc animated:YES];
  vc.settingsButton.hidden = YES;
  [vc release];
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
  [self view];
  [self createAccountButtonPressed:createAccountButton_];
  signUpFullNameTextField_.text = self.fullName;
  signUpUsernameTextField_.text = self.username;
  signUpEmailTextField_.text = self.email;
  signUpPasswordTextField_.text = self.password;
  signUpPhoneTextField_.text = self.phone;

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

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)picker {
  [self view];
  [self createAccountButtonPressed:createAccountButton_];
  signUpFullNameTextField_.text = self.fullName;
  signUpUsernameTextField_.text = self.username;
  signUpEmailTextField_.text = self.email;
  signUpPasswordTextField_.text = self.password;
  signUpPhoneTextField_.text = self.phone;
  if (self.profilePhoto) {
    userImageView_.imageView.image = self.profilePhoto;
  } else {
    userImageView_.imageView.image = [UIImage imageNamed:@"welcome_profile_placeholder"];
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
  if (textField.superview == signUpScrollView_) {
    confirmButton_.enabled = (signUpFullNameTextField_.text.length &&
                              signUpUsernameTextField_.text.length &&
                              signUpEmailTextField_.text.length &&
                              signUpPasswordTextField_.text.length);
  } else if (textField.superview == signInScrollView_) {
    UIView* nextView = [textField.superview viewWithTag:textField.tag + 1];
    if (nextView) {
      [nextView becomeFirstResponder];
    } else {
      confirmButton_.enabled = (usernameTextField_.text.length &&
                                passwordTextField_.text.length);
    }
  }
  [textField resignFirstResponder];
  return YES;
}

- (IBAction)textFieldEditingChanged:(id)sender {
  if ([sender isEqual:self.usernameTextField]) {
    if (timer_)
      [timer_ invalidate];
  
    self.timer = [NSTimer scheduledTimerWithTimeInterval:0.66
                                                  target:self
                                                selector:@selector(validateUsername)
                                                userInfo:nil
                                                repeats:NO];
  }
}

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  CGFloat xOffset = scrollView.contentOffset.x;
  
  if (xOffset > 1450) 
    [UIView animateWithDuration:0.35 animations:^{
      [createAccountButton_ setBackgroundImage:[UIImage imageNamed:@"create_account_button_active"] forState:normal];
    }];
}

#pragma mark - Validation.

- (void) validateUsername {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedValidateURI delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:self.usernameTextField.text, @"login",
                                                              kClientID, @"client_id",
                                                              kClientSecret, @"client_secret", nil];
  request.method = RKRequestMethodPOST;
  [requestQueue_ addRequest:request];
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest *)request didLoadResponse:(RKResponse *)response {
//  NSLog(@"request: %@ loaded response: %@", request.resourcePath, response.bodyAsString);
  
  if (response.statusCode == 200) {
    NSError* err = nil;
    id body = [response parsedBody:&err];
    if (err) {
      NSLog(@"Parse error for response %@: %@", response, err);
      return;
    }
  
    NSString* primaryColorHex = [body objectForKey:@"color_primary"];
    NSString* secondaryColorHex = [body objectForKey:@"color_secondary"];

    if (primaryColorHex && ![primaryColorHex isEqualToString:@""] && ![secondaryColorHex isEqualToString:@""]) 
        self.validationStamp1ImageView.image = [Util stampImageWithPrimaryColor:primaryColorHex
                                                                secondary:secondaryColorHex];
      if (self.validationStampView.hidden == YES) {
        self.validationStampView.alpha = 0.0;
        self.validationStampView.hidden = NO;
        [UIView animateWithDuration:0.4 animations:^{self.validationStampView.alpha = 1.0;}];
      }
  }
  else {
    if (self.validationStampView.hidden == NO) {
      [UIView animateWithDuration:0.4
                       animations:^{self.validationStampView.alpha = 0.0;}
                       completion:^(BOOL finished){
                         self.validationStampView.hidden = YES;
                         self.validationStampView.alpha = 1.0;
                       }];
    }
  }
}

- (void)request:(RKRequest *)request didFailLoadWithError:(NSError *)error {
  NSLog(@"request: %@ hit error: %@", request.resourcePath, error.code);
}

#pragma mark - RKRequestQueueDelegate methods.

- (void)requestQueue:(RKRequestQueue*)queue willSendRequest:(RKRequest*)request {
  [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
  if (queue == requestQueue_) {
    [RKClient sharedClient].requestQueue.suspended = YES;
  }
}

- (void)requestQueue:(RKRequestQueue*)queue didLoadResponse:(RKResponse*)response {
  if (queue == requestQueue_)
    [RKClient sharedClient].requestQueue.suspended = NO;
}

- (void)requestQueue:(RKRequestQueue*)queue didCancelRequest:(RKRequest*)request {
  if (queue == requestQueue_)
    [RKClient sharedClient].requestQueue.suspended = NO;
}

- (void)requestQueue:(RKRequestQueue*)queue didFailRequest:(RKRequest*)request withError:(NSError*)error {
  if (queue == requestQueue_)
    [RKClient sharedClient].requestQueue.suspended = NO;
}


@end
