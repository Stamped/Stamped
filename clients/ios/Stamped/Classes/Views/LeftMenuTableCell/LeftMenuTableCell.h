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
    UIImageView *_selectedView;
}

@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) NSInteger badgeCount;
@property(nonatomic,assign) BOOL border;
@property(nonatomic,assign) BOOL topBorder;
@property(nonatomic,assign) id delegate;

@end
@protocol LeftMenuTableCellDelegate
- (void)leftMenuTableCellHighlighted:(LeftMenuTableCell*)cell;
@end