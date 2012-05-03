//
//  UIFont+Stamped.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UIFont+Stamped.h"
#import "STConfiguration.h"

@implementation UIFont(Stamped)

+ (UIFont*)stampedTitleFont {
  return [STConfiguration value:@"UIFont.stampedTitleFont"];
}

+ (UIFont*)stampedTitleLightFont {
  return [STConfiguration value:@"UIFont.stampedTitleLightFont"];
}

+ (UIFont*)stampedFont {
  return [STConfiguration value:@"UIFont.stampedFont"];
}

+ (UIFont*)stampedBoldFont {
  return [STConfiguration value:@"UIFont.stampedBoldFont"];
}

+ (UIFont*)stampedSubtitleFont {
  return [STConfiguration value:@"UIFont.stampedSubtitleFont"];
}

+ (UIFont*)stampedTitleFontWithSize:(CGFloat)size {
  return [[UIFont stampedTitleFont] fontWithSize:size];
}

+ (UIFont*)stampedTitleLightFontWithSize:(CGFloat)size {
  return [[UIFont stampedTitleLightFont] fontWithSize:size];
}

+ (UIFont*)stampedBoldFontWithSize:(CGFloat)size {
  return [[UIFont stampedBoldFont] fontWithSize:size];
}

+ (UIFont*)stampedFontWithSize:(CGFloat)size {
  return [[UIFont stampedFont] fontWithSize:size];
}

@end
