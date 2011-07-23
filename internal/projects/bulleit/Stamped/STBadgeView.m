//
//  STBadgeView.m
//  
//
//  Created by Andrew Bonventre on 7/22/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STBadgeView.h"

#import <QuartzCore/QuartzCore.h>

@implementation STBadgeView

@synthesize backgroundImage = backgroundImage_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.layer.cornerRadius = 2.0;
    self.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
    self.textAlignment = UITextAlignmentCenter;
    self.textColor = [UIColor whiteColor];
    self.backgroundImage = [UIImage imageNamed:@"badge_background"];
  }
  return self;
}

- (void)dealloc {
  self.backgroundImage = nil;
  [super dealloc];
}

- (void)drawRect:(CGRect)rect {
  [backgroundImage_ drawInRect:rect];
  [super drawRect:rect];
}

@end
