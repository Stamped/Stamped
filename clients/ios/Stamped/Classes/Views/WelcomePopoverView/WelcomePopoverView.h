//
//  WelcomePopoverView.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <UIKit/UIKit.h>
 
@protocol WelcomePopoverViewDelegate;
@interface WelcomePopoverView : UIImageView {
    UISwipeGestureRecognizer *_swipe;
    UIView *_welcomeView;
    UIView *_optionsView;
    UIView *_container;
    UIButton *_closeButton;
}

@property(nonatomic,assign) id <WelcomePopoverViewDelegate> delegate;

@end

@protocol WelcomePopoverViewDelegate
- (void)welcomePopoverViewSelectedTwitter:(WelcomePopoverView*)view;
- (void)welcomePopoverViewSelectedFacebook:(WelcomePopoverView*)view;
- (void)welcomePopoverViewSelectedEmail:(WelcomePopoverView*)view;
- (void)welcomePopoverViewSelectedLogin:(WelcomePopoverView*)view;
- (void)welcomePopoverViewSelectedClose:(WelcomePopoverView*)view;
@end