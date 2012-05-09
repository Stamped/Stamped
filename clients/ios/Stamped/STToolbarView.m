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
                            (id)[UIColor colorWithWhite:88.0/255 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:39.0/255 alpha:1.0].CGColor, nil];
    gradientLayer.frame = self.bounds;
    [self.layer insertSublayer:gradientLayer atIndex:0];
    [gradientLayer release];
    
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
    self.layer.shadowOpacity = 1;
    //self.layer.borderWidth = 1;
    //self.layer.borderColor = [UIColor colorWithWhite:73.0/255 alpha:1].CGColor;
    self.layer.shadowOffset = CGSizeMake(0, -1);
  }
  return self;
}

- (id)init {
  return [self initWithFrame:CGRectMake(-1, 0, 322, 54)];
}

- (void)packViews:(NSArray*)views withPadding:(CGFloat)padding {
  CGSize totalSize = [Util packViews:views padding:padding vertical:NO uniform:YES];
  CGRect totalFrame = [Util centeredAndBounded:totalSize inFrame:CGRectMake(0, 0, self.frame.size.width, self.frame.size.height)];
  [Util offsetViews:views byX:totalFrame.origin.x andY:totalFrame.origin.y];
  for (UIView* button in views) {
    [self addSubview:button];
  }
}

- (void)packViews:(NSArray*)views {
  [self packViews:views withPadding:10];
}

@end
