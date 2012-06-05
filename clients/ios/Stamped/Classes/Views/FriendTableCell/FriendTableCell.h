//
//  FriendTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView;
@interface FriendTableCell : UITableViewCell {
    STAvatarView *_avatarView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
    UIButton *_actionButton;
    UIView *_stampView;
    
    UIColor *_primaryColor;
    UIColor *_secondaryColor;
}

- (void)setupWithUser:(id<STUser>)user;

@end
