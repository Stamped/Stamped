//
//  STEditEntityTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/29/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STEditEntityTextField.h"

#import "UIColor+Stamped.h"

const CGFloat kTextLeftInset = 10.0;

@implementation STEditEntityTextField

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    self.textColor = [UIColor stampedDarkGrayColor];
  }
  return self;
}

- (CGRect)textRectForBounds:(CGRect)bounds {
  return CGRectOffset(CGRectInset(bounds, kTextLeftInset / 2, 0), kTextLeftInset / 2, 0);
}

- (CGRect)editingRectForBounds:(CGRect)bounds {
  return [self textRectForBounds:bounds];
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.87 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, CGRectGetMaxY(self.bounds) - 1, CGRectGetWidth(self.bounds), 1));
}

@end
