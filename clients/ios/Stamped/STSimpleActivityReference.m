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

- (void)dealloc
{
  [indices_ release];
  [action_ release];
  [format_ release];
  [super dealloc];
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
