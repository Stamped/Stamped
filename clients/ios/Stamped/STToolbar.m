//
//  STToolbar.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STToolbar.h"

#import <QuartzCore/QuartzCore.h>

@implementation STToolbar

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self commonInit];
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self commonInit];
  return self;
}

- (void)commonInit {
  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  gradientLayer.colors = [NSArray arrayWithObjects:
      (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
      (id)[UIColor colorWithWhite:0.855 alpha:1.0].CGColor, nil];
  gradientLayer.frame = self.bounds;
  [self.layer insertSublayer:gradientLayer atIndex:0];
  [gradientLayer release];

  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
  self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
  self.layer.shadowOpacity = 1;
  self.layer.shadowOffset = CGSizeMake(0, -1);
}

@end
