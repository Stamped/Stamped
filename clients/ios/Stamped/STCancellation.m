//
//  STCancellation.m
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCancellation.h"
#import "Util.h"
#import "STImageCache.h"

@interface STCancellationImageGroup : NSObject <STCancellationDelegate>

- (id)initWithImages:(NSArray*)urls withCallback:(void (^)(NSError* error, STCancellation* cancellation))callback;

@property (nonatomic, readonly, retain) STCancellation* cancellation;
@property (nonatomic, readonly, retain) NSMutableArray* imageCancellations;
@property (nonatomic, readwrite, assign) NSInteger count;

@end

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
        //NSLog(@"cancelling: %@", self.decoration);
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

+ (STCancellation*)loadImages:(NSArray*)urls withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  if (urls.count == 0) return [STCancellation dispatchNoopCancellationWithCallback:block];
  return [[[STCancellationImageGroup alloc] initWithImages:urls withCallback:block] autorelease].cancellation;
}

@end

@implementation STCancellationImageGroup

@synthesize cancellation = cancellation_;
@synthesize imageCancellations = imageCancellations_;
@synthesize count = count_;

- (void)cancelAll {
  for (STCancellation* cancellation in self.imageCancellations) {
    [cancellation cancel];
  }
}

- (id)initWithImages:(NSArray*)urls withCallback:(void (^)(NSError* error, STCancellation* cancellation))callback {
  self = [super init];
  if (self) {
    // will be retained until all blocks are discarded (aka. done)
    cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
    imageCancellations_ = [[NSMutableArray alloc] init];
    for (NSString* url in urls) {
      UIImage* cachedImage = [[STImageCache sharedInstance] cachedImageForImageURL:url];
      if (!cachedImage) {
        STCancellation* imageCancellation = [[STImageCache sharedInstance] imageForImageURL:url andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
          if (image) {
            self.count++;
            if (self.count == self.imageCancellations.count) {
              if ([self.cancellation finish] && callback) {
                callback(nil, cancellation_);
              }
            }
          }
          else {
            [self cancelAll];
            if ([self.cancellation finish] && callback) {
              callback(error, cancellation_);
            }
          }
        }];
        [imageCancellations_ addObject:imageCancellation];
      }
    }
    if (imageCancellations_.count == 0) {
      [Util executeOnMainThread:^{
        if ([self.cancellation finish] && callback) {
          callback(nil, cancellation_);
        }
      }];
    }
  }
  return self;
}

- (void)dealloc
{
  cancellation_.delegate = nil;
  [cancellation_ release];
  
  [imageCancellations_ release];
  [super dealloc];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
  NSAssert1(cancellation == self.cancellation, @"Unknown cancellation object %@", cancellation);
  [self cancelAll];
}

@end
