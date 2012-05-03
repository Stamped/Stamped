//
//  STFriendsOfFriendsStampsList.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsOfFriendsStampsList.h"
#import "STStampedAPI.h"

@implementation STFriendsOfFriendsStampsList

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STFriendsOfFriendsStampsList alloc] init];
}

+ (STFriendsOfFriendsStampsList*)sharedInstance {
  return _sharedInstance;
}

- (void)setupSlice {
  STFriendsSlice* friendsSlice = [[[STFriendsSlice alloc] init] autorelease];
  friendsSlice.distance = [NSNumber numberWithInt:2];
  friendsSlice.inclusive = [NSNumber numberWithBool:NO];
   self.genericSlice = friendsSlice;
}

- (id)init {
  self = [super init];
  if (self) {
    [self setupSlice];
  }
  return self;
}

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  return [[STStampedAPI sharedInstance] stampsForFriendsSlice:(id)slice andCallback:block];
}

@end
