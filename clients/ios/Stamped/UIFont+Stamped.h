//
//  UIFont+Stamped.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 Common Stamped fonts and font factories.
 
 Notes:
 This is a very successful category used pervasively throughout the application.
 
 TODOs:
 Extend this category to use the new limited font palette that Anthony developed.
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface UIFont (Stamped)

+ (UIFont*)stampedTitleFont;
+ (UIFont*)stampedTitleLightFont;
+ (UIFont*)stampedFont;
+ (UIFont*)stampedBoldFont;
+ (UIFont*)stampedSubtitleFont;

+ (UIFont*)stampedTitleFontWithSize:(CGFloat)size;
+ (UIFont*)stampedTitleLightFontWithSize:(CGFloat)size;
+ (UIFont*)stampedBoldFontWithSize:(CGFloat)size;
+ (UIFont*)stampedFontWithSize:(CGFloat)size;

@end
