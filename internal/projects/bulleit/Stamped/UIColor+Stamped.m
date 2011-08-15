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

@end
