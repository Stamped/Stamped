//
//  STUserSliceList.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserStampsSliceList.h"
#import "STUserCollectionSlice.h"
#import "STStampedAPI.h"

@implementation STUserStampsSliceList

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  return [[STStampedAPI sharedInstance] stampsForUserSlice:(id)slice andCallback:block];
}

@end
