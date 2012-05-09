//
//  STGenericLazyList.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericLazyList.h"
#import "STCancellation.h"

@interface STGenericLazyListPending : NSObject

- (id)initWithRange:(NSRange)range;

@property (nonatomic, readwrite, assign) NSRange range;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readwrite, retain) NSArray* results;

@end

@implementation STGenericLazyListPending

@synthesize range = range_;
@synthesize cancellation = cancellation_;
@synthesize results = results_;

- (id)initWithRange:(NSRange)range {
  self = [super init];
  if (self) {
    range_ = range;
  }
  return self;
}

- (void)dealloc
{
  [cancellation_ release];
  [results_ release];
  [super dealloc];
}

@end

@interface STGenericLazyList ()

- (void)notifyDelegates:(SEL)selector;
- (void)handlePending:(STGenericLazyListPending*)pending withResults:(NSArray*)results andError:(NSError*)error;

@property (nonatomic, readonly, retain) NSMutableArray* objects;
@property (nonatomic, readonly, retain) NSMutableDictionary* delegates;
@property (nonatomic, readonly, retain) NSMutableArray* pending;
@property (nonatomic, readwrite, assign) BOOL reachedMax;
@property (nonatomic, readwrite, assign) BOOL failed;

@end

@implementation STGenericLazyList

@synthesize objects = objects_;
@synthesize delegates = delegates_;
@synthesize pending = pending_;
@synthesize reachedMax = reachedMax_;
@synthesize failed = failed_;

static const NSInteger _batchSize = 20;

- (id)init
{
  self = [super init];
  if (self) {
    objects_ = [[NSMutableArray alloc] init];
    delegates_ = [[NSMutableDictionary alloc] init];
    pending_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc
{
  [objects_ release];
  [delegates_ release];
  [pending_ release];
  [super dealloc];
}

- (void)growToCount:(NSInteger)count {
  if (!self.failed) {
    NSLog(@"GrowTOCount:%d",count);
    if (self.count < count && !self.reachedMax) {
      NSInteger pendingCount = self.count;
      for (STGenericLazyListPending* pendingObject in self.pending) {
        pendingCount = MAX(pendingCount, pendingObject.range.location + pendingObject.range.length);
      }
      if (pendingCount < count) {
        NSRange range = NSMakeRange(pendingCount, count - pendingCount);
        NSLog(@"RequestingRange:%d,%d",range.location, range.length);
        STGenericLazyListPending* pendingObject = [[[STGenericLazyListPending alloc] initWithRange:range] autorelease];
        STCancellation* cancellation = [self fetchWithRange:range andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation2) {
          [self handlePending:pendingObject withResults:results andError:error];
        }];
        pendingObject.cancellation = cancellation;
        [self.pending addObject:pendingObject];
      }
    }
  }
}

- (void)handlePending:(STGenericLazyListPending*)pendingObject withResults:(NSArray*)results andError:(NSError*)error {
  NSLog(@"HandlePending:%@,%@",results, error);
  if (results) {
    pendingObject.results = results;
    BOOL modified = NO;
    BOOL endReached = NO;
    while (!endReached) {
      STGenericLazyListPending* consumed = nil;
      for (STGenericLazyListPending* aPending in self.pending) {
        if (aPending.results && aPending.range.location <= self.count) {
          NSAssert1(aPending.range.location == self.count, @"Pending range starts before count for %@", self);
          [self.objects addObjectsFromArray:aPending.results];
          consumed = aPending;
          if (self.objects.count < aPending.range.location + aPending.range.length) {
            endReached = YES;
            self.reachedMax = YES;
          }
          modified = YES;
          break;
        }
      }
      if (consumed) {
        [self.pending removeObject:consumed];
      }
      else {
        break;
      }
    }
    if (endReached) {
      [self cancelPendingRequests];
    }
    if (modified) {
      [self notifyDelegates:@selector(lazyListDidGrow:)];
    }
    if (endReached) {
      [self notifyDelegates:@selector(lazyListDidReachMaxCount:)];
    }
  }
  else {
    [self cancelPendingRequests];
    self.failed = YES;
    [self notifyDelegates:@selector(lazyListDidFail:)];
  }
}

- (void)shrinkToCount:(NSInteger)count {
  self.reachedMax = NO;
  if (self.count > count) {
    NSRange range = NSMakeRange(count, self.count - count);
    [self.objects removeObjectsInRange:range];
  }
  [self notifyDelegates:@selector(lazyListDidShrink:)];
}

- (id)objectAtIndex:(NSInteger)index {
  if (self.count > index) {
    return [self.objects objectAtIndex:index];
  }
  else {
    return nil;
  }
}

- (void)prepareRange:(NSRange)range {
  NSInteger count = range.location + range.length;
  if (count > self.count) {
    [self growToCount:count];
  }
}

- (void)reload {
  self.failed = NO;
  self.reachedMax = NO;
  NSInteger count = self.count;
  [self cancelPendingRequests];
  [self notifyDelegates:@selector(lazyListWillReload:)];
  [self shrinkToCount:0];
  [self growToCount:count];
}

- (void)cancelPendingRequests {
  NSLog(@"Cancelling pending operations");
  for (STGenericLazyListPending* pendingObject in self.pending) {
    [pendingObject.cancellation cancel];
  }
  [self.pending removeAllObjects];
}

- (void)addDelegate:(id<STLazyListDelegate>)delegate {
  NSValue* pointerValue = [NSValue valueWithPointer:delegate];
  NSInteger count = [[self.delegates objectForKey:pointerValue] integerValue];
  count++;
  [self.delegates setObject:[NSNumber numberWithInteger:count] forKey:pointerValue];
}

- (void)removeDelegate:(id<STLazyListDelegate>)delegate {
  NSValue* pointerValue = [NSValue valueWithPointer:delegate];
  NSInteger count = [[self.delegates objectForKey:pointerValue] integerValue];
  count--;
  NSAssert1(count >= 0, @"Tried to remove a delegate that is not present %@", delegate);
  if (count > 0) {
    [self.delegates setObject:[NSNumber numberWithInteger:count] forKey:pointerValue];
  }
  else {
    [self.delegates removeObjectForKey:pointerValue];
  }
}

- (NSInteger)count {
  return self.objects.count;
}

- (void)notifyDelegates:(SEL)selector {
  for (NSValue* pointerValue in self.delegates) {
    id<STLazyListDelegate> delegate = [pointerValue pointerValue];
    NSInteger count = [[self.delegates objectForKey:pointerValue] integerValue];
    for (NSInteger i = 0; i < count; i++) {
      if ([delegate respondsToSelector:selector]) {
        [delegate performSelector:selector withObject:self];
      }
    }
  }
}

- (STCancellation*)fetchWithRange:(NSRange)range
                      andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  NSAssert1(NO, @"Fetch must be implemented in subclass: %@", self);
  return nil;
}

@end
