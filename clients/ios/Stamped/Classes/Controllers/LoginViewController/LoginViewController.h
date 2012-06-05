//
//  LoginViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/23/12.
//
//

#import <UIKit/UIKit.h>

@protocol LoginViewControllerDelegate;
@class LoginTextView, LoginKeyboardButton, LoginLoadingView;
@interface LoginViewController : UIViewController {
    LoginTextView *_textView;
    UIImageView *_stampedImageView;
    LoginKeyboardButton *_loginButton;
    LoginLoadingView *_loadingView;
}
@property(nonatomic,assign) id <LoginViewControllerDelegate> delegate;
@property(nonatomic,assign,getter = isLoading) BOOL loading;

- (void)animateIn;

@end
@protocol LoginViewControllerDelegate
- (void)loginViewControllerDidDismiss:(LoginViewController*)controller;
@end