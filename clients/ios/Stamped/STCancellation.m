//
//  STCancellation.m
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCancellation.h"
#import "Util.h"

@implementation STCancellation

@synthesize cancelled = cancelled_;
@synthesize delegate = delegate_;
@synthesize decoration = decoration_;

- (id)init
{
  self = [super init];
  if (self) {
  }
  return self;
}

- (void)dealloc
{
  [decoration_ release];
  [super dealloc];
}

- (BOOL)cancelled {
  @synchronized (self) {
    return cancelled_;
  }
}

- (void)cancel {
  @synchronized (self) {
    if (!cancelled_) {
      cancelled_ = YES;
      if (self.delegate) {
        [self.delegate cancellationWasCancelled:self];
        NSLog(@"cancelling: %@", self.decoration);
      }
    }
  }
}

- (BOOL)finish {
  @synchronized (self) {
    delegate_ = nil;
    return !cancelled_;
  }
}

- (id<STCancellationDelegate>)delegate {
  @synchronized (self) {
    return delegate_;
  }
}

- (void)setDelegate:(id<STCancellationDelegate>)delegate {
  @synchronized (self) {
    delegate_ = delegate;
  }
}

+ (STCancellation*)cancellation {
  return [[[STCancellation alloc] init] autorelease];
}

+ (STCancellation*)cancellationWithDelegate:(id<STCancellationDelegate>)delegate {
  STCancellation* cancellation = [STCancellation cancellation];
  cancellation.delegate = delegate;
  return cancellation;
}

+ (STCancellation*)dispatchNoopCancellationWithCallback:(void (^)(NSError*, STCancellation*))block {
  STCancellation* cancellation = [STCancellation cancellation];
  [Util executeOnMainThread:^{
    if ([cancellation finish]) {
      block(nil, cancellation);
    }
  }];
  cancellation.decoration = @"no-op";
  return cancellation;
}

@end
