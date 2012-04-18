//
//  STFriendsSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsSource.h"
#import "Util.h"
#import "STInboxViewController.h"

@implementation STFriendsSource

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
    [self.delegate shouldSetScopeTo:STStampedAPIScopeFriendsOfFriends];
  }
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

@end
