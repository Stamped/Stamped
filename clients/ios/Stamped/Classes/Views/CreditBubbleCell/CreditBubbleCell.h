//
//  CreditBubbleCell.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>
#import "UserStampView.h"

@interface CreditBubbleCell : UIControl {
    UIImageView *_background;
}

- (void)deselect;

@property(nonatomic,retain,readonly) UILabel *titleLabel;
@property(nonatomic,retain,readonly) UserStampView *stampView;

@end
