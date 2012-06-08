//
//  SettingsTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import <UIKit/UIKit.h>

@interface SettingsTableCell : UITableViewCell {
    UIView *_topBorder;
    UIView *_bottomBorder;
    UIView *_background;
}

@property(nonatomic,retain) UILabel *titleLabel;

- (void)setFirst:(BOOL)first last:(BOOL)last;

@end
