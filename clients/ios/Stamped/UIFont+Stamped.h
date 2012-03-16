//
//  UIFont+Stamped.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface UIFont (Stamped)


+ (UIFont*)stampedTitleFontWithSize:(CGFloat)size;
+ (UIFont*)stampedBoldFontWithSize:(CGFloat)size;
+ (UIFont*)stampedFontWithSize:(CGFloat)size;

@end
