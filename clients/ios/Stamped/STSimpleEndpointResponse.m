//
//  STSimpleEndpointResponse.m
//  Stamped
//
//  Created by Landon Judkins on 5/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEndpointResponse.h"
#import "STSimpleAction.h"

@implementation STSimpleEndpointResponse

@synthesize action = action_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
  }
  return self;
}

- (void)dealloc
{
  [action_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.action forKey:@"action"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEndpointResponse class]];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
