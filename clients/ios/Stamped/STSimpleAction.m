//
//  STSimpleAction.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleAction.h"
#import "STSimpleSource.h"

@implementation STSimpleAction

@synthesize action = action_;
@synthesize name = name_;
@synthesize sources = sources_;

- (void)dealloc {
  self.action = nil;
  self.name = nil;
  self.sources = nil;
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleAction class]];
  
  [mapping mapAttributes:
   @"action",
   @"name",
   nil];
  
  [mapping mapRelationship:@"sources" withMapping:[STSimpleSource mapping]];
  
  return mapping;
}

@end
