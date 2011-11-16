//
//  STSectionHeaderView.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STSectionHeaderView.h"

#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"

@implementation STSectionHeaderView

@synthesize leftLabel = leftLabel_;
@synthesize rightLabel = rightLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
    gradientLayer.frame = frame;
    gradientLayer.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.87 alpha:0.9].CGColor,
       (id)[UIColor colorWithWhite:0.94 alpha:0.9].CGColor, nil];
    [self.layer addSublayer:gradientLayer];
    [gradientLayer release];
    
    leftLabel_ = [[UILabel alloc] initWithFrame:CGRectOffset(frame, 9, 0)];
    leftLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    leftLabel_.shadowColor = [UIColor whiteColor];
    leftLabel_.shadowOffset = CGSizeMake(0, 1);
    leftLabel_.textColor = [UIColor stampedGrayColor];
    leftLabel_.backgroundColor = [UIColor clearColor];
    [self addSubview:leftLabel_];
    [leftLabel_ release];
    
    rightLabel_ = [[UILabel alloc] initWithFrame:CGRectOffset(frame, -9, 0)];
    rightLabel_.textAlignment = UITextAlignmentRight;
    rightLabel_.textColor = [UIColor stampedGrayColor];
    rightLabel_.shadowColor = [UIColor whiteColor];
    rightLabel_.shadowOffset = CGSizeMake(0, 1);
    rightLabel_.backgroundColor = [UIColor clearColor];
    rightLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self addSubview:rightLabel_];
    [rightLabel_ release];
    
    UIView* bottomBorder = [[UIView alloc] initWithFrame:frame];
    bottomBorder.backgroundColor = [UIColor colorWithWhite:0.88 alpha:1.0];
    CGRect bottomBorderFrame = frame;
    bottomBorderFrame.size.height = 1;
    bottomBorderFrame.origin.y = CGRectGetHeight(frame) - 1;
    bottomBorder.frame = bottomBorderFrame;
    [self addSubview:bottomBorder];
    [bottomBorder release];
    
  }
  return self;
}

@end
