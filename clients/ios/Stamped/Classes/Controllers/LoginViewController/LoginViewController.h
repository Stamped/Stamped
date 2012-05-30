//
//  LoginViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/23/12.
//
//

#import <UIKit/UIKit.h>

@class LoginTextView, LoginKeyboardButton;
@interface LoginViewController : UIViewController {
    LoginTextView *_textView;
    UIImageView *_stampedImageView;
    LoginKeyboardButton *_loginButton;
}
@property(nonatomic,assign,getter = isLoading) BOOL loading;
@end
