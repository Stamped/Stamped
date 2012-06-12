//
//  STDefaultTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import <UIKit/UIKit.h>

@interface STDefaultTableCell : UITableViewCell {
    UIView *_topBorder;
    UIView *_bottomBorder;
    UIView *_background;
    UIImageView *_disclosureView;
}

@property(nonatomic,retain,readonly) UILabel *titleLabel;
@property(nonatomic,assign) BOOL showsDisclosure;

- (void)setFirst:(BOOL)first last:(BOOL)last;

@end
