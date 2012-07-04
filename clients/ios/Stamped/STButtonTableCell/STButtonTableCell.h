//
//  STButtonTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import <UIKit/UIKit.h>

@protocol STButtonTableCellDelegate;
@interface STButtonTableCell : UITableViewCell

@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,retain) UILabel *detailTitleLabel;
@property(nonatomic,assign) id delegate;

@end
@protocol STButtonTableCellDelegate
- (void)stButtonTableCellSelected:(STButtonTableCell*)cell;
@end