//
//  STTextViewTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import <UIKit/UIKit.h>

@protocol STTextViewTableCellDelegate;
@interface STTextViewTableCell : UITableViewCell

@property(nonatomic,assign) id <STTextViewTableCellDelegate> delegate;
@property(nonatomic,retain) UITextView *textView;
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) CGFloat lastHeight;

+ (CGFloat)heightForText:(NSString*)text;
- (CGFloat)height;

@end
@protocol STTextViewTableCellDelegate
- (void)stTextViewTableCellDidBeginEditing:(STTextViewTableCell*)cell;
- (void)stTextViewTableCellDidEndEditing:(STTextViewTableCell*)cell;
- (void)stTextViewTableCell:(STTextViewTableCell*)cell heightChangedFrom:(CGFloat)height to:(CGFloat)newHeight;
- (void)stTextViewTableCell:(STTextViewTableCell*)cell textChanged:(UITextView *)textView;
@end