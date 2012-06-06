//
//  UIColor+Stamped.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "UIColor+Stamped.h"
#import "STConfiguration.h"

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

@end
