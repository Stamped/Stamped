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

- (void)dealloc
{
  [action_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEndpointResponse class]];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
