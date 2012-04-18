//
//  STSimpleStampedBy.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampedBy.h"
#import "STSimpleStampedByGroup.h"

@implementation STSimpleStampedBy

@synthesize friends = _friends;
@synthesize friendsOfFriends = _friendsOfFriends;
@synthesize everyone = _everyone;

- (void)dealloc
{
  [_friends release];
  [_friendsOfFriends release];
  [_everyone release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleStampedBy class]];
  
  [mapping mapRelationship:@"friends" withMapping:[STSimpleStampedByGroup mapping]];
  [mapping mapKeyPath:@"fof" toRelationship:@"friendsOfFriends" withMapping:[STSimpleStampedByGroup mapping]];
  [mapping mapKeyPath:@"all" toRelationship:@"everyone" withMapping:[STSimpleStampedByGroup mapping]];
  
  return mapping;
}

@end
