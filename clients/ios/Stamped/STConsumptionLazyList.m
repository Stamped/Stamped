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

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  NSLog(@"Consumption:%@,%@",slice.offset, slice.limit);
  return [[STStampedAPI sharedInstance] stampsForFriendsSlice:(id)slice andCallback:block];
}

@end
