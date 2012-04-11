//
//  STFriendsOfFriendsSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsOfFriendsSource.h"
#import "STStampedAPI.h"

@implementation STFriendsOfFriendsSource

- (void)setSlice:(STGenericCollectionSlice *)slice {
  STFriendsSlice* friendsSlice = [[[STFriendsSlice alloc] init] autorelease];
  [friendsSlice importDictionaryParams:[slice asDictionaryParams]];
  friendsSlice.distance = [NSNumber numberWithInt:2];
  friendsSlice.inclusive = [NSNumber numberWithBool:NO];
  [super setSlice:friendsSlice];
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForFriendsSlice:(id)slice andCallback:block];
}

@end
