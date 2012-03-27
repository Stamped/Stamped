//
//  STWeakProxy.m
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STWeakProxy.h"

@implementation STWeakProxy

@synthesize value = _value;

- (id)initWithValue:(id)value {
  self = [super init];
  if (self) {
    _value = value;
  }
  return self;
}

@end
