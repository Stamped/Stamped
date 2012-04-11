//
//  STSuggestedSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSuggestedSource.h"
#import "STStampedAPI.h"

@implementation STSuggestedSource

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForSuggestedSlice:slice andCallback:block];
}

@end
