//
//  STRippleViewContainer.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRippleViewContainer.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"

@interface STRippleViewContainer ()

- (void)addGradientBackground:(UIView*) view primaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor;

@end

@implementation STRippleViewContainer

@synthesize body = _body;

- (id)initWithDelegate:(id<STViewDelegate>)delegate
          primaryColor:(NSString*)primaryColor 
     andSecondaryColor:(NSString*)secondaryColor {
  self = [super initWithDelegate:delegate andFrame:CGRectMake(5, 0, 310, 0)];
  if (self) {
    CALayer* layer = self.layer;
    layer.shadowColor = [UIColor blackColor].CGColor;
    layer.shadowOpacity = .05;
    layer.shadowRadius = 1.0;
    layer.shadowOffset = CGSizeMake(0, 1);
    
    
    UIImageView* topRipple = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_detail_ripple_top"]] autorelease];
    [self appendChildView:topRipple];
    
    _body = [[STViewContainer alloc] initWithDelegate:self andFrame:CGRectMake(0, 0, self.frame.size.width, 0)];
    //_body.backgroundColor = [UIColor whiteColor];
    [self appendChildView:_body];
    
    UIImageView* bottomRipple = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_detail_ripple_bottom"]] autorelease];
    [self appendChildView:bottomRipple];
    
    [self addGradientBackground:self primaryColor:primaryColor andSecondaryColor:secondaryColor];
  }
  return self;
}


- (void)addGradientBackground:(UIView*)view primaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor {
  secondaryColor = @"337711";
  CAGradientLayer* gradient = [[[CAGradientLayer alloc] init] autorelease];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (secondaryColor) {
    [Util splitHexString:secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  gradient.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.9].CGColor,
                     (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.9].CGColor,
                     nil];
  gradient.bounds = view.layer.bounds;
  gradient.startPoint = CGPointMake(-.5,-.5);
  gradient.endPoint = CGPointMake(.5, .5);
  gradient.anchorPoint = CGPointMake(0, 0);
  gradient.position = CGPointMake(0, 0);
  [view.layer insertSublayer:gradient atIndex:0];
}

@end
