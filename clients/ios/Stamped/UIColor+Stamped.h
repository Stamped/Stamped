//
//  UIColor+Stamped.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

/*
 Contains common colors, gradients, and conversion functions.
 
 Notes:
 This is a pervasive and successful category used throughout the application.
 I strongly recommend its continued use.
 
 TODOs:
 Expand color palette to encompass new design palette.
 Fix color picker and remove insaneHexString method.
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface UIColor (Stamped)

+ (UIColor*)stampedBlackColor;
+ (UIColor*)stampedDarkGrayColor;
+ (UIColor*)stampedGrayColor;
+ (UIColor*)stampedLightGrayColor;
+ (UIColor*)stampedLinkColor;
+ (NSArray*)stampedLightGradient;
+ (NSArray*)stampedGradient;
+ (NSArray*)stampedDarkGradient;
+ (NSArray*)stampedBlueGradient;
+ (NSArray*)stampedButtonGradient;

- (NSString*)hexString;
- (NSString*)insaneHexString __attribute__ ((deprecated)); //support for transparency hack in color picker, DO NOT USE IN NEW CODE

+ (UIColor*)stampedColorWithHex:(NSString*)hex andAlpha:(CGFloat)alpha;
+ (UIColor*)stampedColorWithHex:(NSString*)hex;

@end
