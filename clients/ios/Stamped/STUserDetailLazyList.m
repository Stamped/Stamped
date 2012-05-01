//
//  STUserDetailLazyList.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserDetailLazyList.h"
#import "STStampedAPI.h"
#import "Util.h"

@interface STUserDetailLazyList ()

@property (nonatomic, readonly, retain) NSArray* userIDs;

@end

@implementation STUserDetailLazyList

@synthesize userIDs = userIDs_;

- (id)initWithUserIDs:(NSArray*)userIDs {
  self = [super init];
  if (self) {
    userIDs_ = [userIDs retain];
  }
  return self;
}

- (void)dealloc
{
  [userIDs_ release];
  [super dealloc];
}

- (STCancellation*)fetchWithRange:(NSRange)range
                      andCallback:(void (^)(NSArray*, NSError*, STCancellation*))block {
  if (range.location >= self.userIDs.count) {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block([NSArray array], nil, cancellation);
      }
    }];
    return cancellation;
  }
  else {
    NSRange adjustedRange = range;
    if (adjustedRange.location + adjustedRange.length > self.userIDs.count) {
      adjustedRange.length = self.userIDs.count - adjustedRange.location;
    }
    NSArray* batch = [self.userIDs subarrayWithRange:adjustedRange];
    return [[STStampedAPI sharedInstance] userDetailsForUserIDs:batch andCallback:^(NSArray<STUserDetail> *userDetails, NSError *error, STCancellation* cancellation) {
      block(userDetails, error, cancellation);
    }];
  }
}

@end
