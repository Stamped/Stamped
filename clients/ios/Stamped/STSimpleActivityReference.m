//
//  STSimpleActivityReference.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivityReference.h"
#import "STSimpleAction.h"

@implementation STSimpleActivityReference

@synthesize indices = indices_;
@synthesize action = action_;
@synthesize format = format_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    indices_ = [[decoder decodeObjectForKey:@"indices"] retain];
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
    format_ = [[decoder decodeObjectForKey:@"format"] retain];
  }
  return self;
}

- (void)dealloc
{
  [indices_ release];
  [action_ release];
  [format_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.indices forKey:@"indices"];
  [encoder encodeObject:self.action forKey:@"action"];
  [encoder encodeObject:self.format forKey:@"format"];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivityReference class]];
  
  [mapping mapAttributes:
   @"indices",
   @"format",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
