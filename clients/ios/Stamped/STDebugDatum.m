//
//  STDebugDatum.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDebugDatum.h"

@implementation STDebugDatum

@synthesize object = object_;
@synthesize created = created_;

- (id)initWithObject:(id)object {
  self = [super init];
  if (self) {
    object_ = [object retain];
    created_ = [[NSDate date] retain];
  }
  return self;
}

@end
