//
//  STUserSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserSource.h"
#import "STFriendsSlice.h"
#import "STStampedAPI.h"
#import "STUserCollectionSlice.h"
#import "AccountManager.h"

@implementation STUserSource

- (void)setSlice:(STGenericCollectionSlice *)slice {
  STUserCollectionSlice* friendsSlice = [[[STUserCollectionSlice alloc] init] autorelease];
  [friendsSlice importDictionaryParams:[slice asDictionaryParams]];
  friendsSlice.userID = [[STStampedAPI sharedInstance] currentUser].userID;
  [super setSlice:friendsSlice];
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForUserSlice:(id)slice andCallback:block];
}

@end
