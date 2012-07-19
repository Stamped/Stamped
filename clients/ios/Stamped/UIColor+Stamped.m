//
//  UIColor+Stamped.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "UIColor+Stamped.h"
#import "STConfiguration.h"
#import "Util.h"

@implementation UIColor (Stamped)

+ (UIColor*)stampedBlackColor {
    return [STConfiguration value:@"UIColor.stampedBlackColor"];
}

+ (UIColor*)stampedDarkGrayColor {
    return [STConfiguration value:@"UIColor.stampedDarkGrayColor"];
}

+ (UIColor*)stampedGrayColor {
    return [STConfiguration value:@"UIColor.stampedGrayColor"];
}

+ (UIColor*)stampedLightGrayColor {
    return [STConfiguration value:@"UIColor.stampedLightGrayColor"];
}

+ (UIColor*)stampedLinkColor {
    return [STConfiguration value:@"UIColor.stampedLinkColor"];
}

+ (NSArray*)stampedLightGradient {
    return [NSArray arrayWithObjects:[STConfiguration value:@"UIColor.stampedLightGradientStart"], 
            [STConfiguration value:@"UIColor.stampedLightGradientEnd"],
            nil];
}

+ (NSArray*)stampedGradient {
    return [NSArray arrayWithObjects:[STConfiguration value:@"UIColor.stampedGradientStart"], 
            [STConfiguration value:@"UIColor.stampedGradientEnd"],
            nil];
}

+ (NSArray*)stampedDarkGradient {
    return [NSArray arrayWithObjects:[STConfiguration value:@"UIColor.stampedDarkGradientStart"], 
            [STConfiguration value:@"UIColor.stampedDarkGradientEnd"],
            nil];
}

+ (NSArray*)stampedBlueGradient {
    return [NSArray arrayWithObjects:[STConfiguration value:@"UIColor.stampedBlueGradientStart"], 
            [STConfiguration value:@"UIColor.stampedBlueGradientEnd"],
            nil];
}

+ (NSArray*)stampedButtonGradient {
    return [STConfiguration value:@"UIColor.buttonGradient"];
}

- (NSString*)insaneHexString {
    
    const CGFloat *color = CGColorGetComponents([self CGColor]);
    
    CGFloat alpha = color[3];
    CGFloat whiteComp = 255. * (1 - alpha);
    NSInteger r = MIN(color[0] * 255. * alpha + whiteComp , 255.);
    NSInteger g = MIN(color[1] * 255. * alpha + whiteComp , 255.);
    NSInteger b = MIN(color[2] * 255. * alpha + whiteComp , 255.);
    //NSLog(@"comps;%ld, %d, %d, %d, %f, %f, %f", CGColorGetNumberOfComponents([self CGColor]), r, g, b, color[0], color[1], color[2]);
    
    return [NSString stringWithFormat:@"%02x%02x%02x", r, g, b];
}

- (NSString*)hexString {
    
    const CGFloat *color = CGColorGetComponents([self CGColor]);
    
    NSInteger r = color[0] * 255.;
    NSInteger g = color[1] * 255.;
    NSInteger b = color[2] * 255.;
//    NSLog(@"comps;%ld, %d, %d, %d, %f, %f, %f", CGColorGetNumberOfComponents([self CGColor]), r, g, b, color[0], color[1], color[2]);
    
    return [NSString stringWithFormat:@"%02x%02x%02x", r, g, b];
    
}

+ (UIColor*)stampedColorWithHex:(NSString*)hex andAlpha:(CGFloat)alpha {
    CGFloat rgb[3];
    [Util splitHexString:hex toRGB:rgb];
    return [UIColor colorWithRed:rgb[0] green:rgb[1] blue:rgb[2] alpha:alpha];
}

+ (UIColor*)stampedColorWithHex:(NSString *)hex {
    return [self stampedColorWithHex:hex andAlpha:1.0];
}

@end
