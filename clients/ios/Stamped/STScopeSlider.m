//
//  STScopeSlider.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STScopeSlider.h"

typedef enum {
  STScopeSliderGranularityYou = 0,
  STScopeSliderGranularityFriends,
  STScopeSliderGranularityFriendsOfFriends,
  STScopeSliderGranularityEveryone
} STScopeSliderGranularity;

@interface STScopeSlider ()
- (void)commonInit;
- (void)valueChanged:(id)sender;
- (void)dragEnded:(id)sender;
- (void)updateImage;

@property (nonatomic, assign) STScopeSliderGranularity granularity;
@end

@implementation STScopeSlider

@synthesize granularity = granularity_;

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self commonInit];

  return self;
}

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self commonInit];
  
  return self;
}

- (void)commonInit {
  self.granularity = STScopeSliderGranularityFriends;
  [self setMinimumTrackImage:[UIImage imageNamed:@"scope_track"] forState:UIControlStateNormal];
  [self setMaximumTrackImage:[UIImage imageNamed:@"scope_track"] forState:UIControlStateNormal];
  [self addTarget:self action:@selector(valueChanged:) forControlEvents:UIControlEventValueChanged];
  [self addTarget:self action:@selector(dragEnded:) forControlEvents:(UIControlEventTouchUpInside | UIControlEventTouchUpOutside | UIControlEventTouchCancel)];
}

- (void)valueChanged:(id)sender {

}

- (void)dragEnded:(id)sender {
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  self.granularity = quotient;
  [self setValue:(0.333 * quotient) animated:YES];
}

- (void)setGranularity:(STScopeSliderGranularity)granularity {
  if (granularity != granularity_) {
    granularity_ = granularity;
    [self updateImage];
  }
}

- (void)updateImage {
  UIImage* background = [UIImage imageNamed:@"scope_drag_outer"];
  UIGraphicsBeginImageContextWithOptions(background.size, NO, 0.0);
//  CGContextRef context = UIGraphicsGetCurrentContext();
  [background drawInRect:CGRectMake(0, 0, background.size.width, background.size.height)];
  UIImage* final = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  [self setThumbImage:final forState:UIControlStateNormal];
}

@end
