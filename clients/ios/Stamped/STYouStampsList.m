//
//  STYouStampsList.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STYouStampsList.h"
#import "STUserCollectionSlice.h"
#import "STStampedAPI.h"

@implementation STYouStampsList

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STYouStampsList alloc] init];
}

+ (STYouStampsList *)sharedInstance {
  return _sharedInstance;
}

- (void)setupSlice {
  STUserCollectionSlice* slice = [[[STUserCollectionSlice alloc] init] autorelease];
  slice.userID = [[STStampedAPI sharedInstance] currentUser].userID;
  self.genericSlice = slice;
}

- (id)init {
  self = [super init];
  if (self) {
    [self setupSlice];
  }
  return self;
}

@end
