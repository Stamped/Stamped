//
//  STRippleBar.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRippleBar.h"

#import <QuartzCore/QuartzCore.h>
#import "Util.h"

@implementation STRippleBar

- (void)averageRGB:(CGFloat*)destination withRGB:(CGFloat*)other {
  for (int i = 0; i < 3; i++) {
    destination[i] = (destination[i]+other[i]) / 2;
  }
}

- (void)addGradientBackground:(UIView*)view primaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor isTop:(BOOL)isTop {
  CAGradientLayer* gradient = [[[CAGradientLayer alloc] init] autorelease];
  CGFloat rgb[2][3];
  [Util splitHexString:primaryColor toRGB:rgb[0]];
  
  if (secondaryColor) {
    [Util splitHexString:secondaryColor toRGB:rgb[1]];
    if (isTop) {
      [self averageRGB:rgb[1] withRGB:rgb[0]];
    }
    else {
      [self averageRGB:rgb[0] withRGB:rgb[1]];
    }
  }
  else {
    for (NSInteger i = 0; i < 3; i++) {
      rgb[1][0] = rgb[0][0];
    }
  }
  gradient.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithRed:rgb[0][0] green:rgb[0][1] blue:rgb[0][2] alpha:0.9].CGColor,
                     (id)[UIColor colorWithRed:rgb[1][0] green:rgb[1][1] blue:rgb[1][2] alpha:0.9].CGColor,
                     nil];
  gradient.bounds = view.layer.bounds;
  gradient.anchorPoint = CGPointMake(0, 0);
  gradient.position = CGPointMake(0, 0);
  gradient.startPoint = CGPointMake(0,.5);
  gradient.endPoint = CGPointMake(1,.5);
  [view.layer insertSublayer:gradient atIndex:0];
}

- (id)initWithPrimaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor isTop:(BOOL)isTop {
  return [self initWithFrame:CGRectMake(0, 0, 310, 3.5) andPrimaryColor:primaryColor andSecondaryColor:secondaryColor isTop:isTop];
}

- (id)initWithFrame:(CGRect)frame andPrimaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor isTop:(BOOL)isTop
{
  NSString* imagePath = @"stamp_detail_ripple_top";
  if (!isTop) {
    imagePath = @"stamp_detail_ripple_bottom";
  }
  self = [super initWithFrame:frame];
  if (self) {
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imagePath]] autorelease];
    imageView.frame = CGRectMake(0, 0, frame.size.width, frame.size.height);
    [self addGradientBackground:self primaryColor:primaryColor andSecondaryColor:secondaryColor isTop:isTop];
    [self addSubview:imageView];
  }
  return self;
}

+ (NSString*)grayColor {
    return @"dcdcdc";
}

@end
