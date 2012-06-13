//
//  EditProfileFooterView.h
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import <UIKit/UIKit.h>

@protocol EditProfileFooterViewDelegate;
@interface EditProfileFooterView : UIView
@property(nonatomic,assign) id <EditProfileFooterViewDelegate> delegate;

@end
@protocol EditProfileFooterViewDelegate
- (void)editProfileFooterViewDeleteAccount:(EditProfileFooterView*)view;
@end