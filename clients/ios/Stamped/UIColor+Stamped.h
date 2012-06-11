//
//  UIColor+Stamped.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

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

@end
