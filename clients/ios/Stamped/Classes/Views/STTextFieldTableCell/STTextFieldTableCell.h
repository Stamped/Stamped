//
//  STTextFieldTableCell.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@interface STTextFieldTableCell : UITableViewCell
@property(nonatomic,readonly,strong) UITextField *textField;
@property(nonatomic,readonly,strong) UILabel *titleLabel;

- (void)disable;
- (void)enable;

@end
