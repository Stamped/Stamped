//
//  FirstRunViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>
#import <UIKit/UIKit.h>

@class UserImageView;
@class FirstRunViewController;

@protocol FirstRunViewControllerDelegate

- (void)viewController:(FirstRunViewController*)viewController
    didReceiveUsername:(NSString*)username
              password:(NSString*)password;

- (void)viewController:(FirstRunViewController*)viewController
willCreateUserWithName:(NSString*)name
              username:(NSString*)handle
              password:(NSString*)password
                 email:(NSString*)email
          profileImage:(UIImage*)image
           phoneNumber:(NSString*)number;

@end

@interface FirstRunViewController : UIViewController <UITextFieldDelegate,
                                                      UINavigationControllerDelegate,
                                                      UIImagePickerControllerDelegate,
                                                      UIActionSheetDelegate,
                                                      UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIView* bottomView;
@property (nonatomic, retain) IBOutlet UIView* animationContentView;
@property (nonatomic, retain) IBOutlet UIButton* signInButton;
@property (nonatomic, retain) IBOutlet UIButton* createAccountButton;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;
@property (nonatomic, retain) IBOutlet UIButton* confirmButton;
@property (nonatomic, retain) IBOutlet UIScrollView* signInScrollView;
@property (nonatomic, retain) IBOutlet UIImageView* stampedLogo;
@property (nonatomic, retain) IBOutlet UITextField* usernameTextField;
@property (nonatomic, retain) IBOutlet UITextField* passwordTextField;
@property (nonatomic, retain) IBOutlet UIScrollView* signUpScrollView;
@property (nonatomic, retain) IBOutlet UITextField* signUpFullNameTextField;
@property (nonatomic, retain) IBOutlet UITextField* signUpUsernameTextField;
@property (nonatomic, retain) IBOutlet UITextField* signUpEmailTextField;
@property (nonatomic, retain) IBOutlet UITextField* signUpPasswordTextField;
@property (nonatomic, retain) IBOutlet UITextField* signUpPhoneTextField;
@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* activityIndicator;
@property (nonatomic, assign) id<FirstRunViewControllerDelegate> delegate;

- (IBAction)createAccountButtonPressed:(id)sender;
- (IBAction)signInButtonPressed:(id)sender;
- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)confirmButtonPressed:(id)sender;
- (IBAction)takePhotoButtonPressed:(id)sender;

- (void)signInFailed:(NSString*)reason;

- (void)signUpSucess;
- (void)signUpFailed:(NSString*)reason;

@end

