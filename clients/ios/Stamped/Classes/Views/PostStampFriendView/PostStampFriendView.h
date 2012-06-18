//
//  PostStampFriendView.h
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView;
@interface PostStampFriendView : UIControl {
    STAvatarView *_avatarView;
    UILabel *_titleLabel;
    UIImageView *_borderView;

}

@property(nonatomic,readonly,retain) id <STUser> user;
@property(nonatomic,retain) id <STStamp> stamp;

- (void)setupWithUser:(id<STUser>)user index:(NSInteger)index;

@end
