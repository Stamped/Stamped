//
//  STNavigationBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STNavigationBar.h"


@implementation STNavigationBar

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.85 alpha:1.0].CGColor);
  CGContextFillRect(ctx, rect);
  [[UIImage imageNamed:@"nav_bar"] drawInRect:rect];
}

@end
