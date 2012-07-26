//
//  LeftMenuLargeCell.h
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "LeftMenuTableCell.h"

@interface LeftMenuLargeCell : UITableViewCell {
    STBlockUIView *_iconView;
    UIImageView *_selectedView;
    UIView *_highlightedView;
    
    UIView *_topBorder;
    UIView *_bottomBorder;
}


@property(nonatomic,retain) UIImage *icon;
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,assign) BOOL border;
@property(nonatomic,assign) id delegate;

- (void)setTop:(BOOL)top bottom:(BOOL)bottom;

@end
