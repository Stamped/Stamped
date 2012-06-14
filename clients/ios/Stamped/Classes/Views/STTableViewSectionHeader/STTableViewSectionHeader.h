//
//  STTableHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>

@interface STTableViewSectionHeader : UIImageView

@property(nonatomic,readonly,retain) UILabel *titleLabel;

+ (CGFloat)height;

@end
