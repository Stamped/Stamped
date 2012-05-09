//
//  STEveryoneStampsList.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEveryoneStampsList.h"
#import "STStampedAPI.h"
#import "STConfiguration.h"

@implementation STEveryoneStampsList

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STEveryoneStampsList alloc] init];
}

+ (STEveryoneStampsList*)sharedInstance {
  return _sharedInstance;
}

- (void)setupSlice {
  self.genericSlice = [[[STGenericCollectionSlice alloc] init] autorelease];
}

- (void)reload {
  if (self == [STEveryoneStampsList sharedInstance]) {
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
  return [[STStampedAPI sharedInstance] stampsForSuggestedSlice:(id)slice andCallback:block];
}

@end
