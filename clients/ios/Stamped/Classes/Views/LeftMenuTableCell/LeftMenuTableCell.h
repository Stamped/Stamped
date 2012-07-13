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
@property (nonatomic, readwrite, retain) UIImage* whiteIcon;
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) NSInteger badgeCount;
@property(nonatomic,assign) BOOL border;
@property(nonatomic,assign) id delegate;

- (void)setTop:(BOOL)top bottom:(BOOL)bottom;
- (void)countUpdated:(id)notImportant;

@end
@protocol LeftMenuTableCellDelegate
- (void)leftMenuTableCellHighlighted:(UITableViewCell*)cell highlighted:(BOOL)highlighted;
@end