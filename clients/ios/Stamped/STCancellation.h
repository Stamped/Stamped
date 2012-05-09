//
//  STCancellation.h
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@class STCancellation;

@protocol STCancellationDelegate <NSObject>

- (void)cancellationWasCancelled:(STCancellation*)cancellation;

@end

@interface STCancellation : NSObject

- (void)cancel;
- (BOOL)finish;

@property (readonly, assign) BOOL cancelled;
@property (readwrite, assign) id<STCancellationDelegate> delegate;
@property (readwrite, copy) NSString* decoration;

+ (STCancellation*)cancellation;

+ (STCancellation*)cancellationWithDelegate:(id<STCancellationDelegate>)delegate;

+ (STCancellation*)dispatchNoopCancellationWithCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

+ (STCancellation*)loadImages:(NSArray*)urls withCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

@end
