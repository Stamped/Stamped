//
//  STSimpleActionItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActionItem.h"
#import "STSimpleAction.h"

@implementation STSimpleActionItem

@synthesize icon = icon_;
@synthesize name = name_;
@synthesize action = action_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
  }
  return self;
}

- (void)dealloc {
  self.name = nil;
  self.icon = nil;
  self.action = nil;
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.icon forKey:@"icon"];
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.action forKey:@"action"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActionItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"icon",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
