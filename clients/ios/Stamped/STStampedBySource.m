//
//  STStampedBySource.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedBySource.h"

@implementation STStampedBySource

- (void)setSlice:(STGenericCollectionSlice *)slice {
  NSAssert([slice isMemberOfClass:[STStampedBySlice class]], @"slice must be a STStampedBySlice");
  STStampedBySlice* stampedBySlice = (STStampedBySlice*)slice;
  NSAssert(stampedBySlice.group, @"stampedBy.group must be set");
  [super setSlice:slice];
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampedByForStampedBySlice:(STStampedBySlice*)slice andCallback:^(id<STStampedBy> stampedBy, NSError* error) {\
    id<STStampedByGroup> group = stampedBy.friends;
    if (!group) group = stampedBy.friendsOfFriends;
    if (!group) group = stampedBy.everyone;
    block(group.stamps, error);
  }];
}

@end
