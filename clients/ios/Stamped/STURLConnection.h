//
//  STURLConnection.h
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCancellation.h"

@interface STURLConnection : NSObject

- (id)initWithURL:(NSURL*)url andCallback:(void(^)(NSData* data, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readonly, retain) STCancellation* cancellation;

+ (STCancellation*)cancellationWithURL:(NSURL*)url andCallback:(void(^)(NSData* data, NSError* error, STCancellation* cancellation))block;

@end
