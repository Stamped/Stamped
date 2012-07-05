//
//  CreditUserTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>
#import "STUser.h"

@class STAvatarView, UserStampView;
@interface CreditUserTableCell : UITableViewCell {
    STAvatarView *_avatarView;
    UserStampView *_stampView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
    UIImageView *_checkView;
}

@property(nonatomic,assign) BOOL checked;

- (void)setupWithUser:(id<STUser>)user;

@end
