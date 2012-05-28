//
//  STWelcomeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <UIKit/UIKit.h>

@protocol STWelcomeViewControllerDelegate;
@class WelcomePopoverView;
@interface STWelcomeViewController : UIViewController {
    WelcomePopoverView *_popoverView;
}

@property(nonatomic,assign) id <STWelcomeViewControllerDelegate> delegate;
- (void)animateIn;

@end
@protocol STWelcomeViewControllerDelegate
@end
