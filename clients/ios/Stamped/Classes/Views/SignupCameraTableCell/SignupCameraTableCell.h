//
//  SignupCameraTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import <UIKit/UIKit.h>

@protocol SignupCameraCellDelegate;
@interface SignupCameraTableCell : UITableViewCell

@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) id <SignupCameraCellDelegate> delegate;

@end
@protocol SignupCameraCellDelegate
- (void)signupCameraTableCellChoosePhoto:(SignupCameraTableCell*)cell;
@end