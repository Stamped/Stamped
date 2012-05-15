//
//  STAbstractModelSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCacheModelSource.h"
#import "Util.h"

@interface STCacheModelSource ()

@property (nonatomic, readonly, retain) NSCache* cache;

@end

@implementation STCacheModelSource

@synthesize delegate = _delegate;
@synthesize cache = _cache;
@dynamic maximumCost;

+ (NSString*)errorDomain {
  return @"STCacheModelSource";
}

- (id)initWithDelegate:(id<STCacheModelSourceDelegate>)delegate {
  self = [super init];
  if (self) {
    _cache = [[NSCache alloc] init];
    [_cache setTotalCostLimit:NSIntegerMax];
    _delegate = delegate;
  }
  return self;
}

- (void)setMaximumCost:(NSInteger)maximumCost {
  [self.cache setTotalCostLimit:maximumCost];
}

- (NSInteger)maximumCost {
  return self.cache.totalCostLimit;
}

- (void)setObject:(id)object forKey:(NSString*)key {
  [_cache setObject:object forKey:key];
}

- (void)removeObjectForKey:(NSString*)key {
  [_cache removeObjectForKey:key];
}

- (STCancellation*)cacheWithKey:(NSString*)key callback:(void(^)(id, NSError*, STCancellation*))block {
  return [self fetchWithKey:key callback:block];
}

- (STCancellation*)updateWithKey:(NSString*)key callback:(void(^)(id, NSError*, STCancellation*))block {
  id object = [self.cache objectForKey:key];
  id<STCacheModelSourceDelegate> delegate = self.delegate;
  if (delegate) {
    STCancellation* cancellation = [delegate objectForCache:self 
                                                    withKey:key 
                                           andCurrentObject:object 
                                               withCallback:^(id model, NSInteger cost, NSError* error, STCancellation* cancellation2) {
                                                 if (model) {
                                                   [self.cache setObject:model forKey:key cost:cost];
                                                 }
                                                 if (!cancellation2.cancelled) {
                                                   block(model, error, cancellation2);
                                                 }
                                               }];
    return cancellation;
  }
  else {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(nil, [NSError errorWithDomain:[STCacheModelSource errorDomain] 
                                       code:STCacheModelSourceErrorNoDelegate 
                                   userInfo:[NSDictionary dictionary]], cancellation);
      }
    }];
    return cancellation;
  }
}

- (STCancellation*)fetchWithKey:(NSString*)key callback:(void(^)(id model, NSError* error, STCancellation* cancellation))block {
  id object = [self.cache objectForKey:key];
  if (object) {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(object, nil, cancellation);
      }
    }];
    return cancellation;
  }
  else {
    return [self updateWithKey:key callback:block];
  }
}

- (id)cachedValueForKey:(NSString*)key {
  return [self.cache objectForKey:key];
}

- (void)fastPurge {
  [self.cache removeAllObjects];
}

@end
