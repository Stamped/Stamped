//
//  STWelcomeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    STWelcomeViewControllerOptionLogin = 0,
    STWelcomeViewControllerOptionSignup,
    STWelcomeViewControllerOptionTwitter,
    STWelcomeViewControllerOptionFacebook,
} STWelcomeViewControllerOption;

@protocol STWelcomeViewControllerDelegate;
@class WelcomePopoverView;
@interface STWelcomeViewController : UIViewController {
    WelcomePopoverView *_popoverView;
}

@property(nonatomic,assign) id <STWelcomeViewControllerDelegate> delegate;

- (void)animateIn;
- (void)popIn;
- (void)showSignIn;

@end
@protocol STWelcomeViewControllerDelegate
- (void)stWelcomeViewControllerDismiss:(STWelcomeViewController*)controller;
- (void)stWelcomeViewController:(STWelcomeViewController*)controller selectedOption:(STWelcomeViewControllerOption)option;
@end
