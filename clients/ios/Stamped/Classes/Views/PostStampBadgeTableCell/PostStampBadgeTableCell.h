//
//  PostStampBadgeTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import <UIKit/UIKit.h>
#import "STBadge.h"

@protocol PostStampBadgeTableCell;
@interface PostStampBadgeTableCell : UITableViewCell {
    UIImageView *_badgeImageView;
    UILabel *_titleLabel;
    UILabel *_midTitleLabel;
    UILabel *_detailTitleLabel;
    UIImageView *_shadowView;
    UIView *_borderView;
}

@property(nonatomic,assign) id <PostStampBadgeTableCell> delegate;

- (void)setupWithBadge:(id<STBadge>)badge;
- (void)showShadow:(BOOL)shadow;

@end

@protocol PostStampBadgeTableCell
- (void)postStampBadgeTableCellShare:(PostStampBadgeTableCell*)cell;
@end