//
//  FriendTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

@protocol FriendTableCellDelegate;
@class STAvatarView, FriendStatusButton, UserStampView;
@interface FriendTableCell : UITableViewCell {
    STAvatarView *_avatarView;
    FriendStatusButton *_actionButton;
    UserStampView *_stampView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
}

- (void)setupWithUser:(id<STUser>)user;
@property(nonatomic,assign) id <FriendTableCellDelegate> delegate;
@end

@protocol FriendTableCellDelegate
- (void)friendTableCellToggleFollowing:(FriendTableCell*)cell;
@end