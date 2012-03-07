//
//  STDetailScroller.m
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDetailScroller.h"

@interface STDetailScroller ()
- (void)commonInit;
@end

@implementation STDetailScroller

#pragma mark - Private Methods.

- (void)commonInit {
  self.pagingEnabled = YES;
}

#pragma mark - Public Methods.

- (id)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if (self) {
      [self commonInit];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)coder {
  self = [super initWithCoder:coder];
  if (self) {
    [self commonInit];
  }
  return self;
}

/*
// Only override drawRect: if you perform custom drawing.
// An empty implementation adversely affects performance during animation.
- (void)drawRect:(CGRect)rect
{
    // Drawing code
}
*/

@end
