//
//  STCancellation.h
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 
 Cancellations are used as the return value for almost all cancellable asynchronous operations.
 
 Cancellations are based on a simple pattern that is used pervasively in this project:
 
 Conventions:
 Asynchronous operation invocations return cancellations.
 The callback blocks of these functions generally take the form:
    void (^)(A_TYPE result, NSError* error, STCancellation* cancellation)
 The callback is guaranteed not be called synchrounously
 The callback is guaranteed to be called on the main thread (if called).
 The callback is guaranteed to be called if not cancelled.
 The callback is guaranteed NOT to be called if cancelled on the main thread.
 However, cancellation doesn't guarantee transactional execution of the task (which would be a big restriction).
 
 Notes:
 Cancellations were chosen over NSOperation mostly for their simplicity. From a receiver perspective,
 cancellations are trivially simple objects and can be ignored if not used. From a asynch implementation
 perspective, cancellations offer three main implementation patterns, listed in order starting with the most
 frequently used:
 
 Return the cancellation from the lower-level async operation on which the operation is based.
 Return a cancellation just as a wrapper around a boolean cancelled field.
 Return a cancellation that uses a delegate to trigger cancel notification to the operation implementation.
 
 In this project, most base level IO operations (caching, API calls, URLs) return cancellations that use 
 the delegate strategy to respond to cancellation appropriately. Higher level functions wrap these cancellations
 and transparently return the root cancellation from the underlying IO operation. In some cases, simpler implementations
 use a delegate-less cancellation just to ensure that the callback won't be called after cancellation, but they
 do not respond to the cancel signal directly.
 
 2012-08-10
 -Landon
 */

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
