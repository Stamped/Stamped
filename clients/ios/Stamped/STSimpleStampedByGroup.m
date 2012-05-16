//
//  STSimpleStampedByGroup.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampedByGroup.h"
#import "STSimpleStamp.h"

@implementation STSimpleStampedByGroup

@synthesize count = _count;
@synthesize stamps = _stamps;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _count = [[decoder decodeObjectForKey:@"count"] retain];
    _stamps = [[decoder decodeObjectForKey:@"stamps"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_count release];
  [_stamps release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.count forKey:@"count"];
  [encoder encodeObject:self.stamps forKey:@"stamps"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleStampedByGroup class]];
  
  [mapping mapAttributes:
   @"count",
   nil];
  
  [mapping mapRelationship:@"stamps" withMapping:[STSimpleStamp mapping]];
  
  return mapping;
}

@end
