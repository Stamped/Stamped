//
//  STNavigationBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STNavigationBar.h"

#import <QuartzCore/QuartzCore.h>

@interface STNavigationBar ()
- (void)initialize;
@end

@implementation STNavigationBar

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];
  
  return self;
}

// Loaded from a nib.
- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];
  
  return self;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.85 alpha:1.0].CGColor);
  CGContextFillRect(ctx, rect);
  [[UIImage imageNamed:@"nav_bar"] drawInRect:rect];
}

- (void)initialize {
  CGFloat ripplesY = CGRectGetMaxY(self.bounds);
  CALayer* ripplesLayer = [[CALayer alloc] init];
  ripplesLayer.frame = CGRectMake(0, ripplesY, 320, 3);
  ripplesLayer.contentsGravity = kCAGravityResizeAspect;
  ripplesLayer.contents = (id)[UIImage imageNamed:@"nav_bar_ripple"].CGImage;
  [self.layer addSublayer:ripplesLayer];
  self.layer.masksToBounds = NO;
  [ripplesLayer release];
}

@end
