//
//  StampDetailAddCommentView.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/18/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailAddCommentView.h"

@implementation StampDetailAddCommentView

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.9 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, 0, CGRectGetWidth(self.bounds), 1));
  CGContextRestoreGState(ctx);
}

@end
