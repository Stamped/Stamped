//
//  STConsumptionLazyList.m
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionLazyList.h"
#import "STStampedAPI.h"

@implementation STConsumptionLazyList

- (void)setGenericSlice:(STGenericSlice *)genericSlice {
  //NSLog(@"consumptionSlice:%@",genericSlice);
  NSAssert1([genericSlice isMemberOfClass:[STConsumptionSlice class]], @"slice must be a consumption slice; was %@", genericSlice);
  [super setGenericSlice:genericSlice];
}

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  //NSLog(@"Consumption:%@,%@",slice.offset, slice.limit);
  return [[STStampedAPI sharedInstance] stampsForConsumptionSlice:(id)slice andCallback:block];
}

@end
