//
//  FriendTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView, FriendStatusButton, UserStampView;
@interface FriendTableCell : UITableViewCell {
    STAvatarView *_avatarView;
    FriendStatusButton *_actionButton;
    UserStampView *_stampView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
}

- (void)setupWithUser:(id<STUser>)user;

@end
