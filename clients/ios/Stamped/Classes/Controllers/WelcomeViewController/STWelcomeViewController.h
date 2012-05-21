//
//  STWelcomeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <UIKit/UIKit.h>

@class WelcomePopoverView;
@interface STWelcomeViewController : UIViewController {
    WelcomePopoverView *_popoverView;
}

- (void)animateIn;

@end
