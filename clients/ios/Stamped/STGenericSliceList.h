//
//  STGenericSliceList.h
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STLazyList.h"
#import "STGenericSlice.h"
#import "STCancellation.h"
#import "STGenericLazyList.h"

@interface STGenericSliceList : STGenericLazyList

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readwrite, retain) STGenericSlice* genericSlice;

@end
