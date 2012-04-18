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

- (void)setSlice:(STGenericCollectionSlice *)slice {
  STUserCollectionSlice* friendsSlice = [[[STUserCollectionSlice alloc] init] autorelease];
  [friendsSlice importDictionaryParams:[slice asDictionaryParams]];
  friendsSlice.userID = [[STStampedAPI sharedInstance] currentUser].userID;
  [super setSlice:friendsSlice];
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForUserSlice:(id)slice andCallback:block];
}

- (NSString *)lastCellText {
  if (!self.slice.query) {
    return @"Find something to Stamp";
  }
  else {
    return @"Broaden your Scope";
  }
}

- (NSString *)noStampsText {
  return self.lastCellText;
}

- (void)selectedLastCell {
  if (!self.slice.query) {
    /*
     TODO repair
    UINavigationController* controller = [Util sharedNavigationController];
    [controller pushViewController:[[[SearchEntitiesViewController alloc] initWithNibName:@"SearchEntitiesViewController" bundle:nil] autorelease]
                          animated:YES];
     */
  }
  else {
    [self.delegate shouldSetScopeTo:STStampedAPIScopeFriends];
  }
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

@end
