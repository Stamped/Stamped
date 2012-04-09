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
