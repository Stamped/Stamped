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
}

@end
