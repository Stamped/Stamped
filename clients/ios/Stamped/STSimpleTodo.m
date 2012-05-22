//
//  STSimpleTodo.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleTodo.h"
#import "STSimpleEntity.h"
#import "STSimpleStamp.h"

@implementation STSimpleTodo

@synthesize todoID = _todoID;
@synthesize userID = _userID;
@synthesize entity = _entity;
@synthesize stamp = _stamp;
@synthesize created = _created;
@synthesize complete = _complete;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _todoID = [[decoder decodeObjectForKey:@"todoID"] retain];
    _userID = [[decoder decodeObjectForKey:@"userID"] retain];
    _entity = [[decoder decodeObjectForKey:@"entity"] retain];
    _stamp = [[decoder decodeObjectForKey:@"stamp"] retain];
    _created = [[decoder decodeObjectForKey:@"created"] retain];
    _complete = [[decoder decodeObjectForKey:@"complete"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_todoID release];
  [_userID release];
  [_entity release];
  [_stamp release];
  [_created release];
  [_complete release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.todoID forKey:@"todoID"];
  [encoder encodeObject:self.userID forKey:@"userID"];
  [encoder encodeObject:self.entity forKey:@"entity"];
  [encoder encodeObject:self.stamp forKey:@"stamp"];
  [encoder encodeObject:self.created forKey:@"created"];
  [encoder encodeObject:self.complete forKey:@"complete"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleTodo class]];
  
  [mapping mapKeyPathsToAttributes:
   @"favorite_id", @"todoID",
   @"user_id", @"userID",
   nil];
  
  [mapping mapAttributes:
   @"created",
   @"complete",
   nil];
  
  [mapping mapRelationship:@"entity" withMapping:[STSimpleEntity mapping]];
  [mapping mapRelationship:@"stamp" withMapping:[STSimpleStamp mapping]];
  
  return mapping;
}

@end
