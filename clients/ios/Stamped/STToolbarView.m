//
//  STToolbarView.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbarView.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"

@implementation STToolbarView

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
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
  return self;
}

- (void)packViews:(NSArray*)views withPadding:(CGFloat)padding {
  CGSize totalSize = [Util packViews:views padding:padding vertical:NO uniform:YES];
  CGRect totalFrame = [Util centeredAndBounded:totalSize inFrame:self.frame];
  [Util offsetViews:views byX:totalFrame.origin.x andY:totalFrame.origin.y];
  for (UIView* button in views) {
    [self addSubview:button];
  }
}

@end
