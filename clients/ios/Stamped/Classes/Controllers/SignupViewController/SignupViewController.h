//
//  SignupViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@protocol SignupViewControllerDelegate;
@interface SignupViewController : UITableViewController {
    NSArray *_dataSource;
}
@property (nonatomic,assign) id <SignupViewControllerDelegate> delegate;

@end
@protocol SignupViewControllerDelegate
- (void)signupViewControllerCancelled:(SignupViewController*)controller;
@end