//
//  STYouSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STYouSource.h"
#import "STSimpleUser.h"
#import "STEntitySearchController.h"
#import "Util.h"
#import "STStampedAPI.h"

@implementation STYouSource

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
    UINavigationController* controller = [Util sharedNavigationController];
    [controller pushViewController:[[[STEntitySearchController alloc] initWithCategory:self.slice.category 
                                                                              andQuery:self.slice.query] autorelease]
                          animated:YES];
  }
  else {
    [self.delegate shouldSetScopeTo:STStampedAPIScopeFriends];
  }
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

- (NSString*)userID {
  return STStampedAPI.sharedInstance.currentUser.userID;
}

@end
