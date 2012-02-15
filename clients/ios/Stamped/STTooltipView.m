//
//  STTooltipView.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTooltipView.h"

#import <QuartzCore/QuartzCore.h>

@implementation STTooltipView

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.layer.shadowOpacity = 0.4;
    self.layer.shadowOffset = CGSizeMake(0, 2.0);
    self.backgroundColor = [UIColor clearColor];
  }
  return self;
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  CGRect pathRect = CGRectOffset(CGRectInset(self.bounds, 0, 2), 0, -2);
  UIBezierPath* path = [UIBezierPath bezierPath];
  [path moveToPoint:CGPointMake(CGRectGetMidX(pathRect), CGRectGetMaxY(self.bounds))];
  [path addLineToPoint:CGPointMake(CGRectGetMidX(pathRect) - 4, CGRectGetMaxY(pathRect))];
  [path addLineToPoint:CGPointMake(CGRectGetMinX(pathRect) + 4, CGRectGetMaxY(pathRect))];
  [path addArcWithCenter:CGPointMake(CGRectGetMinX(pathRect) + 4, CGRectGetMaxY(pathRect) - 4)
                  radius:4
              startAngle:M_PI_2
                endAngle:M_PI
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMinX(pathRect), CGRectGetMinY(pathRect) + 4)];
  [path addArcWithCenter:CGPointMake(CGRectGetMinX(pathRect) + 4, CGRectGetMinY(pathRect) + 4)
                  radius:4
              startAngle:M_PI
                endAngle:-M_PI_2
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMaxX(pathRect) - 4, CGRectGetMinY(pathRect))];
  [path addArcWithCenter:CGPointMake(CGRectGetMaxX(pathRect) - 4, CGRectGetMinY(pathRect) + 4)
                  radius:4
              startAngle:-M_PI_2
                endAngle:0
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMaxX(pathRect), CGRectGetMaxY(pathRect) - 4)];
  [path addArcWithCenter:CGPointMake(CGRectGetMaxX(pathRect) - 4, CGRectGetMaxY(pathRect) - 4)
                  radius:4
              startAngle:0
                endAngle:M_PI_2
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMidX(pathRect) + 4, CGRectGetMaxY(pathRect))];
  [path closePath];
  CGContextRef context = UIGraphicsGetCurrentContext();
  CGContextAddPath(context, path.CGPath);
  CGContextClip(context);

  CGFloat colors[] = {1, 0, 0, 1.0, 0, 1, 0, 1.0};
  CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
  CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
  CGPoint gradientStartPoint = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMinY(self.bounds));
  CGPoint gradientEndPoint = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMaxY(self.bounds));
  CGContextDrawLinearGradient(context,
                              gradientRef,
                              gradientStartPoint,
                              gradientEndPoint,
                              kCGGradientDrawsAfterEndLocation);
  CGGradientRelease(gradientRef);
  CGColorSpaceRelease(colorSpace);
  [[UIColor whiteColor] setStroke];
  [path stroke];
  self.layer.shadowPath = path.CGPath;
}

@end
