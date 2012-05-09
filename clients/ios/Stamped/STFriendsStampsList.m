//
//  STFriendsStampsList.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsStampsList.h"
#import "STStampedAPI.h"
#import "STConfiguration.h"

@implementation STFriendsStampsList

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STFriendsStampsList alloc] init];
}

+ (STFriendsStampsList*)sharedInstance {
  return _sharedInstance;
}

- (void)setupSlice {
  STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
  self.genericSlice = slice;
}

- (void)reload {
  if (self == [STFriendsStampsList sharedInstance]) {
    self.genericSlice.sort = [STConfiguration value:@"Root.inboxSort"];
  }
  [super reload];
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
  return [[STStampedAPI sharedInstance] stampsForInboxSlice:(id)slice andCallback:block];
}

@end
