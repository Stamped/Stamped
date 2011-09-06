//
//  FirstRunViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>
#import <UIKit/UIKit.h>

@interface FirstRunViewController : UIViewController <UIScrollViewDelegate, UITextFieldDelegate>

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

- (IBAction)createAccountButtonPressed:(id)sender;
- (IBAction)signInButtonPressed:(id)sender;
- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)confirmButtonPressed:(id)sender;

@end
