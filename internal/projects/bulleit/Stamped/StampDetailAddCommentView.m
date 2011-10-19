//
//  StampDetailAddCommentView.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/18/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailAddCommentView.h"

#import <QuartzCore/QuartzCore.h>

@implementation StampDetailAddCommentView

- (void)awakeFromNib {
  self.layer.shadowOffset = CGSizeZero;
  self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.9 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, 0, CGRectGetWidth(self.bounds), 1));
  CGContextRestoreGState(ctx);
}

@end
