//
//  UIColor+Stamped.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "UIColor+Stamped.h"

@implementation UIColor (Stamped)

+ (UIColor*)stampedBlackColor {
  return [UIColor colorWithWhite:0.15 alpha:1.0];
}

+ (UIColor*)stampedDarkGrayColor {
  return [UIColor colorWithWhite:0.35 alpha:1.0];  
}

+ (UIColor*)stampedGrayColor {
  return [UIColor colorWithWhite:0.6 alpha:1.0];
}

+ (UIColor*)stampedLightGrayColor {
  return [UIColor colorWithWhite:0.75 alpha:1.0];
}

+ (UIColor*)stampedLinkColor {
  return [UIColor colorWithRed:.2 green:.2 blue:.7 alpha:1];
}

+ (NSArray*)stampedLightGradient {
  return [NSArray arrayWithObjects:[UIColor colorWithWhite:.99 alpha:1], [UIColor colorWithWhite:.90 alpha:1], nil];
}

+ (NSArray*)stampedGradient {
  return [NSArray arrayWithObjects:[UIColor colorWithWhite:.95 alpha:1], [UIColor colorWithWhite:.85 alpha:1], nil];
}

+ (NSArray*)stampedDarkGradient {
  return [NSArray arrayWithObjects:[UIColor colorWithWhite:.85 alpha:1], [UIColor colorWithWhite:.7 alpha:1], nil];
}

@end
