//
//  EditProfileHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import <UIKit/UIKit.h>
#import "STAvatarView.h"

@protocol EditProfileHeaderViewDelegate;
@class UserStampView, STAvatarView;
@interface EditProfileHeaderView : UIView {
    UIButton *_stampColorButton;
}
@property (nonatomic,assign) id <EditProfileHeaderViewDelegate> delegate;
@property (nonatomic, readwrite, retain) UIImage* image;

- (void)setStampColors:(NSArray*)colors;
- (NSArray*)colors;

@end

@protocol EditProfileHeaderViewDelegate
- (void)editProfileHeaderViewChangePicture:(EditProfileHeaderView*)view;
- (void)editProfileHeaderViewChangeColor:(EditProfileHeaderView*)view;
@end