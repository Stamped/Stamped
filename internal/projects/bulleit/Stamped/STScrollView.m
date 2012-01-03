//
//  STScrollView.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STScrollView.h"

@interface STScrollView ()
- (void)commonInit;
@end

@implementation STScrollView

- (id)initWithCoder:(NSCoder *)aDecoder {
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
  self.delaysContentTouches = NO;
}

- (BOOL)touchesShouldCancelInContentView:(UIView*)view {  
  return YES;
}

- (BOOL)touchesShouldBegin:(NSSet*)touches withEvent:(UIEvent*)event inContentView:(UIView*)view {
  return [super touchesShouldBegin:touches withEvent:event inContentView:view];
}

@end
