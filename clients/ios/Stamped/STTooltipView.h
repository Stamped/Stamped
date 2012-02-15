//
//  STTooltipView.h
//  Stamped
//
//  Created by Andrew Bonventre on 2/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STTooltipView : UIView

- (id)initWithText:(NSString*)text;
- (void)setText:(NSString*)text animated:(BOOL)animated;


@property (nonatomic, readonly) UILabel* textLabel;
@end
