//
//  STFriendsOfFriendsSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsOfFriendsSource.h"
#import "STStampedAPI.h"
#import "Util.h"

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

- (NSString *)lastCellText {
  if (!self.slice.query) {
    return @"Go to Friend Finder";
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
    FindFriendsViewController* findFriends = [[[FindFriendsViewController alloc] initWithNibName:@"FindFriendsView" bundle:nil] autorelease];
    UINavigationController* friendFinder = [[[UINavigationController alloc] initWithRootViewController:findFriends] autorelease];
    [[Util sharedNavigationController] presentModalViewController:friendFinder animated:YES];
    [findFriends didDisplayAsModal];
     */
  }
  else {
    [self.delegate shouldSetScopeTo:STStampedAPIScopeEveryone];
  }
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

@end
