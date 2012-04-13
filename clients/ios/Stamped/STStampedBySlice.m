//
//  STStampedBySlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedBySlice.h"

@implementation STStampedBySlice

@synthesize entityID = _entityID;
@synthesize group = _group;

- (void)dealloc
{
  [_entityID release];
  [_group release];
  [super dealloc];
}

@end
