//
//  UIFont+Stamped.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UIFont+Stamped.h"

@implementation UIFont(Stamped)

+ (UIFont*)stampedTitleFontWithSize:(CGFloat)size {
  return [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:size];
}

+ (UIFont*)stampedBoldFontWithSize:(CGFloat)size {
  return [UIFont fontWithName:@"Helvetica-Bold" size:size];
}

+ (UIFont*)stampedFontWithSize:(CGFloat)size {
  return [UIFont fontWithName:@"Helvetica" size:size];
}

@end
