//
//  STScopeSlider.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STScopeSlider.h"

@interface STScopeSlider ()
- (void)commonInit;
- (void)valueChanged:(id)sender;
@end

@implementation STScopeSlider

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
  [self setMinimumTrackImage:[UIImage imageNamed:@"scope_track"] forState:UIControlStateNormal];
  [self setMaximumTrackImage:[UIImage imageNamed:@"scope_track"] forState:UIControlStateNormal];
  self.continuous = NO;
  [self addTarget:self action:@selector(valueChanged:) forControlEvents:UIControlEventValueChanged];
}

- (void)valueChanged:(id)sender {
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  [self setValue:(0.333 * quotient) animated:YES];
}

- (CGRect)maximumValueImageRectForBounds:(CGRect)bounds {
  CGRect rect = [super maximumValueImageRectForBounds:bounds];
  //NSLog(@"Max drawing rect: %@", NSStringFromCGRect(rect));
  return rect;
}

- (CGRect)minimumValueImageRectForBounds:(CGRect)bounds {
  CGRect rect = [super minimumValueImageRectForBounds:bounds];
  //NSLog(@"Min drawing rect: %@", NSStringFromCGRect(rect));
  return rect;
}

@end
