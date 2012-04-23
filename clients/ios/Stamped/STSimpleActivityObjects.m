//
//  STSimpleActivityObject.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivityObjects.h"
#import "STSimpleUser.h"
#import "STSimpleEntity.h"
#import "STSimpleStamp.h"
#import "STSimpleComment.h"

@implementation STSimpleActivityObjects

@synthesize stamps = stamps_;
@synthesize entities = entities_;
@synthesize users = users_;
@synthesize comments = comments_;

- (void)dealloc
{
  [stamps_ release];
  [entities_ release];
  [users_ release];
  [comments_ release];
  [super dealloc];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivityObjects class]];
  
  [mapping mapRelationship:@"stamps" withMapping:[STSimpleStamp mapping]];
  [mapping mapRelationship:@"entities" withMapping:[STSimpleEntity mapping]];
  [mapping mapRelationship:@"users" withMapping:[STSimpleUser mapping]];
  [mapping mapRelationship:@"comments" withMapping:[STSimpleComment mapping]];
  return mapping;
}

@end
