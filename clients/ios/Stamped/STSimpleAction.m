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
@synthesize name = _name;
@synthesize sources = _sources;

- (id)init
{
  self = [super init];
  if (self) {
    _sources = (NSArray<STSource>*) [[NSArray alloc] init];
  }
  return self;
}

- (void)dealloc {
  [_type release];
  [_name release];
  [_sources release];
  
  [super dealloc];
}

+ (STSimpleAction*)actionWithType:(NSString*)type andSource:(id<STSource>)source {
  STSimpleAction* action = [[[STSimpleAction alloc] init] autorelease];
  action.sources = [NSArray arrayWithObject:source];
  action.type = type;
  return  action;
}

+ (STSimpleAction*)actionWithURLString:(NSString*)url {
  STSimpleSource* source = [[[STSimpleSource alloc] init] autorelease];
  source.link = url;
  return [STSimpleAction actionWithType:@"view" andSource:source];
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
