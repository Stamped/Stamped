//
//  STGenericLazyList.h
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STLazyList.h"
#import "STCancellation.h"

@interface STGenericLazyList : NSObject <STLazyList>

- (STCancellation*)fetchWithRange:(NSRange)range
                      andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readwrite, retain) NSError* lastError;

@end
