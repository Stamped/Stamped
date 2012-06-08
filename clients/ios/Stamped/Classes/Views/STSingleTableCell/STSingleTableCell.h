//
//  STSingleTableCell.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@interface STSingleTableCell : UITableViewCell {
    UIActivityIndicatorView *_activityView;
}

@property(nonatomic,strong) UILabel *titleLabel;
@property(nonatomic,assign,getter = isLoading) BOOL loading;

+ (CGFloat)height;

@end
