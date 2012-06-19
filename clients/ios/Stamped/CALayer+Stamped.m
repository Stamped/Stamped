//
//  CALayer+Stamped.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "CALayer+Stamped.h"
#import "UIColor+Stamped.h"
#import "Util.h"

@implementation CALayer (Stamped)

- (void)useStampedButtonNormalStyle {
  self.borderWidth = 1;
  self.borderColor = [UIColor stampedGrayColor].CGColor;
  self.shadowColor = [UIColor whiteColor].CGColor;
  self.shadowOpacity = .3;
  self.shadowOffset = CGSizeMake(0, 1);
  self.shadowRadius = 1;
  self.cornerRadius = 5;
  self.contentsScale = [[UIScreen mainScreen] scale];
  [Util addGradientToLayer:self withColors:[UIColor stampedGradient] vertical:YES];
}

- (void)useStampedButtonActiveStyle {
  self.borderWidth = 1;
  self.borderColor = [UIColor stampedDarkGrayColor].CGColor;
  self.shadowColor = [UIColor stampedGrayColor].CGColor;
  self.shadowOpacity = .3;
  self.shadowOffset = CGSizeMake(0, 1);
  self.shadowRadius = 1;
  self.cornerRadius = 5;
  self.contentsScale = [[UIScreen mainScreen] scale];
  [Util addGradientToLayer:self withColors:[UIColor stampedDarkGradient] vertical:YES];
}

@end
