//
//  STTabBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STTabBar.h"

@interface STTabBar ()
- (void)initialize;
@end

@implementation STTabBar


- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];
  
  return self;
}

// Loaded from a nib.
- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];

  return self;
}

- (void)initialize {
  //self.backgroundColor = [UIColor clearColor];
}

@end
