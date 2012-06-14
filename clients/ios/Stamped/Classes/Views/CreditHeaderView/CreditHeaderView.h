//
//  CreditHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>
#import "CreditBubbleCell.h"

@protocol CreditHeaderViewDelegate, CreditHeaderViewDataSource;
@interface CreditHeaderView : UIView {
    NSMutableArray *_cells;
    UILabel *_titleLabel;
    UITextField *_textField;
    CGFloat _height;
    UIView *_selectedCell;
    UITextField *_tempTextField;
}

@property(nonatomic,assign) id <CreditHeaderViewDelegate> delegate;
@property(nonatomic,assign) id <CreditHeaderViewDataSource> dataSource;
@property(nonatomic,assign,getter = isEditing) BOOL editing;
@property(nonatomic,readonly,getter = isDeleting) BOOL deleting;

- (void)reloadData;

@end

@protocol CreditHeaderViewDelegate
- (void)creditHeaderViewDidBeginEditing:(CreditHeaderView*)view;
- (void)creditHeaderViewDidEndEditing:(CreditHeaderView*)view;
- (void)creditHeaderViewFrameChanged:(CreditHeaderView*)view;
- (void)creditHeaderView:(CreditHeaderView*)view adjustOffset:(CGPoint)point;
- (void)creditHeaderView:(CreditHeaderView*)view textChanged:(NSString*)text;
@end

@protocol CreditHeaderViewDataSource
- (NSInteger)creditHeaderViewNumberOfCells:(CreditHeaderView*)view;
- (CreditBubbleCell*)creditHeaderView:(CreditHeaderView*)view cellForIndex:(NSInteger)index;
@end