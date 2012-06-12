//
//  STDescriptionTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import <UIKit/UIKit.h>
#import "STDefaultTableCell.h"

@protocol STDescriptionTableCellDelegate;
@interface STDescriptionTableCell : STDefaultTableCell {
    UIButton *_readMoreButton;
}

@property(nonatomic,assign) id <STDescriptionTableCellDelegate> delegate;
@property(nonatomic,retain,readonly) UILabel *detailTitleLabel;
@property(nonatomic,assign,getter=isExpanded) BOOL expanded; // default NO

+ (CGFloat)heightForText:(NSString*)text expanded:(BOOL)expanded;

@end

@protocol STDescriptionTableCellDelegate
- (void)stDescriptionTableCell:(STDescriptionTableCell*)cell didExpand:(BOOL)expanded;
@end