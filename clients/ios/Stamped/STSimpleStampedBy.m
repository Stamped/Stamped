//
//  STSimpleStampedBy.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampedBy.h"

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

@end
