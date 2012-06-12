//
//  STEditProfileViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import <UIKit/UIKit.h>

@protocol STEditProfileViewControllerDelegate;
@interface STEditProfileViewController : UITableViewController {
    NSArray *_dataSource;
}
@property(nonatomic,assign) id <STEditProfileViewControllerDelegate> delegate;

@end
@protocol STEditProfileViewControllerDelegate
- (void)stEditProfileViewControllerCancelled:(STEditProfileViewController*)controller;
- (void)stEditProfileViewControllerSaved:(STEditProfileViewController*)controller;
@end

