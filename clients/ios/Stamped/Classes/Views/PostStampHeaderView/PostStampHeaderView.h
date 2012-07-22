//
//  PostStampHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView, UserStampView;
@interface PostStampHeaderView : UIView

@property(nonatomic,retain) UILabel *titleLabel;
@property (nonatomic, readonly, assign) UIView* stampView;

@end
