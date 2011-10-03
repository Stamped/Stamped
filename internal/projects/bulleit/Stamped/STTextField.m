//
//  STTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/29/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STTextField.h"

#import "UIColor+Stamped.h"

const CGFloat kTextLeftInset = 10.0;

@implementation STTextField

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    self.textColor = [UIColor stampedDarkGrayColor];
    self.keyboardAppearance = UIKeyboardAppearanceAlert;
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
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.866 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, CGRectGetMaxY(self.bounds) - 1, CGRectGetWidth(self.bounds), 1));
}

@end
