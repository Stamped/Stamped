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
#import "Util.h"

@implementation STUserSource

@synthesize userID = userID_;

- (void)dealloc
{
  [userID_ release];
  [super dealloc];
}

- (void)setSlice:(STGenericCollectionSlice *)slice {
  STUserCollectionSlice* friendsSlice = [[[STUserCollectionSlice alloc] init] autorelease];
  [friendsSlice importDictionaryParams:[slice asDictionaryParams]];
  friendsSlice.userID = self.userID;
  [super setSlice:friendsSlice];
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForUserSlice:(id)slice andCallback:block];
}

- (NSString *)lastCellText {
  if (!self.slice.query) {
    return @"No more stamps";
  }
  else {
    return @"No more stamps";
  }
}

- (NSString *)noStampsText {
  return @"No stamps";
}

- (void)selectedLastCell {
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

@end
