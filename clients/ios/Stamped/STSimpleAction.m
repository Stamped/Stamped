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

@synthesize type = _type;
@synthesize name = name_;
@synthesize sources = sources_;

- (void)dealloc {
  [_type release];
  self.name = nil;
  self.sources = nil;
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleAction class]];
  
  [mapping mapAttributes:
   @"type",
   @"name",
   nil];
  
  [mapping mapRelationship:@"sources" withMapping:[STSimpleSource mapping]];
  
  return mapping;
}

@end
