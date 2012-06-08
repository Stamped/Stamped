//
//  TwitterAccountsViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@protocol TwitterAccountsViewControllerDelegate;
@interface TwitterAccountsViewController : UIViewController
@property(nonatomic,assign) id <TwitterAccountsViewControllerDelegate> delegate;
@end

@protocol TwitterAccountsViewControllerDelegate
- (void)twitterAccountsViewControllerSuccessful:(TwitterAccountsViewController*)controller;
- (void)twitterAccountsViewControllerCancelled:(TwitterAccountsViewController*)controller;
@end