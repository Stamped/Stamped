//
//  STSimpleStampedByGroup.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampedByGroup.h"
#import "STSimpleStampPreview.h"

@implementation STSimpleStampedByGroup

@synthesize count = _count;
@synthesize stampPreviews = _stampPreviews;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _count = [[decoder decodeObjectForKey:@"count"] retain];
    _stampPreviews = [[decoder decodeObjectForKey:@"stampPreviews"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_count release];
  [_stampPreviews release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.count forKey:@"count"];
  [encoder encodeObject:self.stampPreviews forKey:@"stampPreviews"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleStampedByGroup class]];
  
  [mapping mapAttributes:
   @"count",
   nil];
  
    [mapping mapKeyPath:@"stamps" toRelationship:@"stampPreviews" withMapping:[STSimpleStampPreview mapping]];
  
  return mapping;
}

@end
