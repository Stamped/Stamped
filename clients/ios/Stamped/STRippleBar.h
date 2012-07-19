//
//  STRippleBar.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#define STRippleBarHeight 3.5

@interface STRippleBar : UIView

- (id)initWithPrimaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor isTop:(BOOL)isTop;

- (id)initWithFrame:(CGRect)frame andPrimaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor isTop:(BOOL)isTop;

+ (NSString*)grayColor;

@end
