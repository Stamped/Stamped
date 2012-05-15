//
//  STSimpleEntitySearchSection.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntitySearchSection.h"
#import "STSimpleEntitySearchResult.h"

@implementation STSimpleEntitySearchSection

@synthesize name = name_;
@synthesize entities = entities_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    entities_ = [[decoder decodeObjectForKey:@"entities"] retain];
  }
  return self;
}

- (void)dealloc
{
  [name_ release];
  [entities_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.entities forKey:@"entities"];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntitySearchSection class]];
  
  [mapping mapAttributes:
   @"name",
   nil];
  
  [mapping mapRelationship:@"entities" withMapping:[STSimpleEntitySearchResult mapping]];
  
  return mapping;
}

@end
