//
//  STHybridCacheSource.m
//  Stamped
//
//  Created by Landon Judkins on 5/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STHybridCacheSource.h"
#import "STPersistentCacheSource.h"
#import "Util.h"

@interface STHybridCacheSource() <NSCacheDelegate, STCancellationDelegate>

@property (nonatomic, readonly, retain) NSCache* cache;
@property (nonatomic, readonly, retain) NSMutableDictionary* cacheDates;
@property (nonatomic, readonly, retain) NSMutableDictionary* cacheKeys;
@property (nonatomic, readwrite, assign) NSInteger persistentCost;
@property (nonatomic, readwrite, copy) NSString* path;
@property (nonatomic, readwrite, retain) NSMutableDictionary* delegateCancellations;
@property (nonatomic, readonly, retain) NSObject* fileLock;

- (NSInteger)modifyPersistentCost:(NSInteger)delta;

@end

@implementation STHybridCacheSource

@synthesize delegate = delegate_;
@synthesize path = path_;
@synthesize maxPersistentCost = maxPersistentCost_;
@synthesize maxAge = maxAge_;
@synthesize cache = cache_;
@synthesize cacheDates = cacheDates_;
@synthesize cacheKeys = cacheKeys_;
@synthesize delegateCancellations = delegateCancellations_;
@synthesize persistentCost = persistentCost_;
@synthesize fileLock = fileLock_;

- (id)initWithCachePath:(NSString*)path relativeToCacheDir:(BOOL)relative {
  self = [super init];
  if (self) {
    path_ = [path copy];
    cache_ = [[NSCache alloc] init];
    cache_.delegate = self;
    cacheDates_ = [[NSMutableDictionary alloc] init];
    cacheKeys_ = [[NSMutableDictionary alloc] init];
    delegateCancellations_ = [[NSMutableDictionary alloc] init];
    fileLock_ = [[NSObject alloc] init];
  }
  return self;
}

- (NSInteger)maxMemoryCount {
  return self.cache.countLimit;
}

- (void)setMaxMemoryCount:(NSInteger)maxMemoryCount {
  self.cache.countLimit = maxMemoryCount;
}

- (id<NSCoding>)fastCachedObjectForKey:(NSString*)key {
  return [self.cache objectForKey:key];
}

- (NSString*)fullPathForKey:(NSString*)key {
  return [NSString stringWithFormat:@"%@/%@", self.path, key];
}

- (BOOL)writeObject:(id<NSCoding>)object withKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  if (![[NSFileManager defaultManager] fileExistsAtPath:self.path]) {
    [[NSFileManager defaultManager] createDirectoryAtPath:self.path withIntermediateDirectories:YES attributes:nil error:nil];
  }
  return [NSKeyedArchiver archiveRootObject:object toFile:fullPath];
}

- (id<NSCoding>)readObjectForKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  return [NSKeyedUnarchiver unarchiveObjectWithFile:fullPath];
}

- (NSNumber*)ageForKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  if (![[NSFileManager defaultManager] fileExistsAtPath:fullPath]) {
    return nil;
  }
  return [NSNumber numberWithInteger:[[[[NSFileManager defaultManager] attributesOfItemAtPath:fullPath error:nil] fileModificationDate] timeIntervalSinceNow]];
}

- (BOOL)isFresh:(NSString*)key {
  NSNumber* age = [self ageForKey:key];
  if (!self.maxAge) {
    return YES;
  }
  if (age && age.doubleValue < self.maxAge.doubleValue) {
    return YES;
  }
  return NO;
}

+ (NSNumber*)ageForPath:(NSString*)path {
  [[NSFileManager defaultManager] attributesOfItemAtPath:path error:nil];
}

- (id<NSCoding>)threadSafeUnarchiveWithPath:(NSString*)path withMaxAge:(NSNumber*)maxAge {
  NSFileManager* manager = [NSFileManager defaultManager];
  
}

- (void)threadSafeArchiveObject:(id<NSCoding>)object withKey:(NSString*)key andDate:(NSDate*)date {
  
}

- (void)threadSafeRemoveWithKey:(NSString*)key {
  @synchronized (self.fileLock) {
    NSFileManager* manager = [NSFileManager defaultManager];
    //NSInteger size = [manager 
  }
}

- (id<NSCoding>)cachedObjectForKey:(NSString*)key {
  id<NSCoding> result = [self fastCachedObjectForKey:key];
  if (!result) {
    //TODO slow fetch
  }
  return result;
}

- (STCancellation*)objectForKey:(NSString*)key 
                    forceUpdate:(BOOL)update 
                   withCallback:(void (^)(id<NSCoding>, NSError*, STCancellation*))block {
  id<NSCoding> fastResult = [self fastCachedObjectForKey:key];
  if (fastResult) {
    STCancellation* fastCancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!fastCancellation.cancelled) {
        block(fastResult, nil, fastCancellation);
      }
    }];
    return fastCancellation;
  }
  else {
    STCancellation* slowCancellation = [STCancellation cancellationWithDelegate:self];
    [Util executeOnMainThread:^{
      id<NSCoding> slowResult = [self cachedObjectForKey:key];
      if (slowResult) {
        if (!slowCancellation.cancelled) {
          block(slowResult, nil, slowCancellation);
        }
      }
      else {
        id cancellationKey = [NSValue valueWithPointer:slowCancellation];
        void (^delegateBlock)(id<NSCoding>, NSError*, STCancellation*) = ^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
          [self.delegateCancellations removeObjectForKey:cancellationKey];
          if (model) {
            [self setObject:model forKey:key];
          }
          if (slowCancellation.finish) {
            block(model, error, slowCancellation);
          }
        };
        STCancellation* delegateCancellation = [self.delegate objectForHybridCache:self
                                                                           withKey:key
                                                                  andCurrentObject:nil
                                                                      withCallback:delegateBlock];
        [self.delegateCancellations setObject:delegateCancellation forKey:cancellationKey];
      }
    }];
    return slowCancellation;
  }
}

- (void)removeObjectForKey:(NSString*)key {
  @synchronized (self) {
    id<NSCoding> cachedObject = [self.cache objectForKey:key];
    [self.cacheDates removeObjectForKey:key];
    if (cachedObject) {
      [self.cacheKeys removeObjectForKey:[NSValue valueWithPointer:cachedObject]];
    }
    [self threadSafeRemoveWithKey:(NSString*)key];
  }
}

- (void)setObject:(id<NSCoding>)object forKey:(NSString*)key {
  @synchronized (self) {
    [self.cacheDates setObject:[NSDate date] forKey:key];
    [self.cacheKeys setObject:key forKey:[NSValue valueWithPointer:object]];
    [self.cache setObject:object forKey:key];
  }
}

- (void)cache:(NSCache *)cache willEvictObject:(id)obj {
  @synchronized (self) {
    NSString* key = [self.cacheKeys objectForKey:[NSValue valueWithPointer:obj]];
    NSDate* date = [self.cacheDates objectForKey:key];
    [self.cacheKeys removeObjectForKey:[NSValue valueWithPointer:obj]];
    [self.cacheDates removeObjectForKey:key];
    if (obj && key && date) {
      [Util executeAsync:^{
        [self threadSafeArchiveObject:obj withKey:key andDate:date];
      }];
    }
  }
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
  id key = [NSValue valueWithPointer:cancellation];
  STCancellation* delegateCancellation = [self.delegateCancellations objectForKey:key];
  [delegateCancellation cancel];
  [self.delegateCancellations removeObjectForKey:key];
}

- (NSInteger)modifyPersistentCost:(NSInteger)delta {
  NSInteger result;
  @synchronized (self) {
    self.persistentCost += delta;
  }
  return result;
}

@end
