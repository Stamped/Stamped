//
//  PostStampHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView, UserStampView;
@interface PostStampHeaderView : UIView {
    UserStampView *_stampView;
}
@property(nonatomic,retain) UILabel *titleLabel;
@end
