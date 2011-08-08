//
//  MediumUserImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/6/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "MediumUserImageView.h"

#import <QuartzCore/QuartzCore.h>

@implementation MediumUserImageView

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:CGRectInset(frame, -2, -2)];
  if (self) {
    self.layer.shadowPath =
        [UIBezierPath bezierPathWithRect:CGRectInset(self.bounds, 2, 2)].CGPath;
    self.layer.shadowOffset = CGSizeZero;
    self.layer.shadowOpacity = 0.4;
    self.layer.shadowRadius = 1.0;
  }
  
  return self;
}

@end
