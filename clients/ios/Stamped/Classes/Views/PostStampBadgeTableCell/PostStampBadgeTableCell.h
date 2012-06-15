//
//  PostStampBadgeTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import <UIKit/UIKit.h>

@interface PostStampBadgeTableCell : UITableViewCell {
    UIImageView *_badgeImageView;
    UILabel *_titleLabel;
    UILabel *_midTitleLabel;
    UILabel *_detailTitleLabel;
    UIImageView *_shadowView;
    UIView *_borderView;
}

- (void)setupWithBadge:(id<STBadge>)badge;
- (void)showShadow:(BOOL)shadow;

@end
