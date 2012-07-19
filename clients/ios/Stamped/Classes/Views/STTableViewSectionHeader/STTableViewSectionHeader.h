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
@property (nonatomic, readwrite, assign) BOOL googleAttribution;
@property (nonatomic, readwrite, retain) UIImageView* googleImage;

+ (CGFloat)height;

@end
