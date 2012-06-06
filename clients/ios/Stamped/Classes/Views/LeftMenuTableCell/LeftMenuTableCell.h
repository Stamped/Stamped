//
//  LeftMenuTableCell.h
//  Stamped
//
//  Created by Devin Doty on 5/21/12.
//
//

#import <UIKit/UIKit.h>

@class STBlockUIView;
@protocol LeftMenuTableCellDelegate;
@interface LeftMenuTableCell : UITableViewCell {
    STBlockUIView *_badgeView;
    STBlockUIView *_iconView;
    UIImageView *_selectedView;
    UIView *_highlightedView;
    
    UIView *_topBorder;
    UIView *_bottomBorder;
}


@property(nonatomic,retain) UIImage *icon;
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) NSInteger badgeCount;
@property(nonatomic,assign) BOOL border;
@property(nonatomic,assign) id delegate;

- (void)setTop:(BOOL)top bottom:(BOOL)bottom;

@end
@protocol LeftMenuTableCellDelegate
- (void)leftMenuTableCellHighlighted:(LeftMenuTableCell*)cell;
@end