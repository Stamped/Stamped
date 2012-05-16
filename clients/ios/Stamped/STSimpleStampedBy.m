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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _friends = [[decoder decodeObjectForKey:@"friends"] retain];
    _friendsOfFriends = [[decoder decodeObjectForKey:@"friendsOfFriends"] retain];
    _everyone = [[decoder decodeObjectForKey:@"everyone"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_friends release];
  [_friendsOfFriends release];
  [_everyone release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.friends forKey:@"friends"];
  [encoder encodeObject:self.friendsOfFriends forKey:@"friendsOfFriends"];
  [encoder encodeObject:self.everyone forKey:@"everyone"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleStampedBy class]];
  
  [mapping mapRelationship:@"friends" withMapping:[STSimpleStampedByGroup mapping]];
  [mapping mapKeyPath:@"fof" toRelationship:@"friendsOfFriends" withMapping:[STSimpleStampedByGroup mapping]];
  [mapping mapKeyPath:@"all" toRelationship:@"everyone" withMapping:[STSimpleStampedByGroup mapping]];
  
  return mapping;
}

@end
