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
#import <RestKit/NSString+MD5.h>
#import <CommonCrypto/CommonDigest.h>


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
@synthesize memoryCost = memoryCost_;

- (id)initWithCachePath:(NSString*)path relativeToCacheDir:(BOOL)relative {
    self = [super init];
    if (self) {
        if (relative) {
            path = [NSString stringWithFormat:@"%@/%@", [Util cacheDirectory].path, path];
        }
        path_ = [path copy];
        cache_ = [[NSCache alloc] init];
        cache_.delegate = self;
        cacheDates_ = [[NSMutableDictionary alloc] init];
        cacheKeys_ = [[NSMutableDictionary alloc] init];
        delegateCancellations_ = [[NSMutableDictionary alloc] init];
        fileLock_ = [[NSObject alloc] init];
        self.memoryCost = ^(id<NSCoding> object) {
            return 1;
        };
    }
    return self;
}

- (void)dealloc
{
    [path_ release];
    [cache_ release];
    [cacheDates_ release];
    [cacheKeys_ release];
    [delegateCancellations_ release];
    [fileLock_ release];
    [super dealloc];
}

- (NSInteger)maxMemoryCost {
    return self.cache.totalCostLimit;
}

- (void)setMaxMemoryCost:(NSInteger)maxMemoryCost {
    self.cache.totalCostLimit = maxMemoryCost;
}

- (NSNumber*)ageFromDate:(NSDate*)date {
    if (date) {
        return [NSNumber numberWithDouble:-[date timeIntervalSinceNow]];
    }
    else {
        return nil;
    }
}

- (id<NSCoding>)fastCachedObjectForKey:(NSString*)key {
    id<NSCoding> result = [self.cache objectForKey:key];
    NSNumber* maxAge = self.maxAge;
    if (result && maxAge) {
        NSDate* date = [self.cacheDates objectForKey:key];
        NSAssert1(date == nil || [date isKindOfClass:[NSDate class]], @"Wrong class for date value %@", date);
        if (!date || [self ageFromDate:date].doubleValue > maxAge.doubleValue) {
            NSLog(@"Removing in memory %@", key);
            result = nil;
            [self.cache removeObjectForKey:key];
            [self removeCacheBookkeepingForObject:result withKey:key];
        }
    }
    return result;
}
/*
 -(NSString*) sha1:(NSString*)input
 {
 const char *cstr = [input cStringUsingEncoding:NSUTF8StringEncoding];
 NSData *data = [NSData dataWithBytes:cstr length:input.length];
 
 uint8_t digest[CC_SHA1_DIGEST_LENGTH];
 
 CC_SHA1(data.bytes, data.length, digest);
 
 NSMutableString* output = [NSMutableString stringWithCapacity:CC_SHA1_DIGEST_LENGTH * 2];
 
 for(int i = 0; i < CC_SHA1_DIGEST_LENGTH; i++)
 [output appendFormat:@"%02x", digest[i]];
 
 return output;
 }
 */
- (NSString*)basePathForKey:(NSString*)key {
    NSString* hash = [key MD5];
    return [NSString stringWithFormat:@"%@/%@", self.path, [hash substringToIndex:2]];
}

- (NSString*)fullPathForKey:(NSString*)key {
    NSString* hash = [key MD5];
    return [NSString stringWithFormat:@"%@/%@/%@", self.path, [hash substringToIndex:2], hash];
}

- (NSNumber*)ageForPath:(NSString*)path {
    if (![[NSFileManager defaultManager] fileExistsAtPath:path]) {
        return nil;
    }
    return [self ageFromDate:[[[NSFileManager defaultManager] attributesOfItemAtPath:path error:nil] fileCreationDate]];
}

- (NSInteger)sizeForPath:(NSString*)path {
    return [[[NSFileManager defaultManager] attributesOfItemAtPath:path error:nil] fileSize];
}

- (id<NSCoding>)threadSafeUnarchiveWithKey:(NSString*)key {
    NSString* fullPath = [self fullPathForKey:key];
    id<NSCoding> result = [NSKeyedUnarchiver unarchiveObjectWithFile:fullPath];
    if (result) {
        [Util executeAsync:^{
            NSDate* date = [[[NSFileManager defaultManager] attributesOfItemAtPath:fullPath error:nil] fileCreationDate];
            NSNumber* age = [self ageFromDate:date];
            //NSLog(@"date:%@, %@",age, self.maxAge);
            if (self.maxAge && age && age.doubleValue > self.maxAge.doubleValue) {
                //NSLog(@"Removing old %@", key);
                [self threadSafeRemoveWithKey:key];
            }
            else {
                [Util executeOnMainThread:^{
                    if (![self.cache objectForKey:key]) {
                        //NSLog(@"Upgrading %@ in %@", [result title], self.path);
                        [self.cache setObject:result forKey:key cost:self.memoryCost(result)];
                        [self.cacheKeys setObject:key forKey:[NSValue valueWithPointer:result]];
                        [self.cacheDates setObject:date forKey:key];
                    }
                }];
            }
        }];
    }
    return result;
}

- (void)threadSafeArchiveObject:(id<NSCoding>)object withKey:(NSString*)key andDate:(NSDate*)date {
    @synchronized (self.fileLock) {
        NSFileManager* manager = [NSFileManager defaultManager];
        NSString* fullPath = [self fullPathForKey:key];
        if ([manager fileExistsAtPath:fullPath]) {
            [self threadSafeRemoveWithKey:key];
        }
        NSString* basePath = [self basePathForKey:key];
        if (![manager fileExistsAtPath:basePath]) {
            NSError* dirError = nil;
            [manager createDirectoryAtPath:basePath withIntermediateDirectories:YES attributes:nil error:&dirError];
            if (dirError) {
                NSLog(@"%@",dirError);
            }
        }
        
        BOOL success = [NSKeyedArchiver archiveRootObject:object toFile:fullPath];
        //NSLog(@"Archived %@ at %@ , %d", object, fullPath, success);
        if (success) {
            [manager setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                                    [NSDate date], NSFileModificationDate,
                                    date, NSFileCreationDate,
                                    nil]
                      ofItemAtPath:fullPath
                             error:nil];
            NSInteger size = [[manager attributesOfItemAtPath:fullPath error:nil] fileSize];
            [self modifyPersistentCost:size];
        }
    }
}

- (void)threadSafeRemoveWithKey:(NSString*)key {
    @synchronized (self.fileLock) {
        NSFileManager* manager = [NSFileManager defaultManager];
        NSString* fullPath = [self fullPathForKey:key];
        NSInteger size = [self sizeForPath:fullPath];
        BOOL success = [manager removeItemAtPath:fullPath error:nil];
        if (success) {
            [self modifyPersistentCost:-size];
        }
    }
}

- (id<NSCoding>)cachedObjectForKey:(NSString*)key {
    id<NSCoding> result = [self fastCachedObjectForKey:key];
    if (!result) {
        result = [self threadSafeUnarchiveWithKey:key];
    }
    return result;
}

- (STCancellation*)objectForKey:(NSString*)key 
                    forceUpdate:(BOOL)update 
               cacheAfterCancel:(BOOL)cacheAfterCancel
                   withCallback:(void (^)(id<NSCoding> model, NSError* error, STCancellation* cancellation))block {
    id<NSCoding> fastResult = nil;
    if (!update && key) {
        fastResult = [self fastCachedObjectForKey:key];
    }
    if (fastResult || !key) {
        //NSLog(@"Fast cached %@ for %@", [fastResult title], self.path);
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
        [Util executeAsync:^{
            id<NSCoding> slowResult = nil;
            if (!update) {
                slowResult = [self cachedObjectForKey:key];
            }
            if (slowResult) {
                [Util executeOnMainThread:^{
                    if (slowCancellation.finish) {
                        block(slowResult, nil, slowCancellation);
                    }
                }];
            }
            else {
                [Util executeOnMainThread:^{
                    id cancellationKey = [NSValue valueWithPointer:slowCancellation];
                    void (^delegateBlock)(id<NSCoding>, NSError*, STCancellation*) = ^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
                        [self.delegateCancellations removeObjectForKey:cancellationKey];
                        if (model) {
                            //NSLog(@"Fetched %@ for %@", [model title], self.path);
                            [self setObject:model forKey:key];
                        }
                        if (slowCancellation.finish) {
                            block(model, error, slowCancellation);
                        }
                    };
                    STCancellation* delegateCancellation = [self.delegate objectForHybridCache:self
                                                                                       withKey:key
                                                                                  withCallback:delegateBlock];
                    NSAssert1(delegateCancellation != nil, @"Cancellation from %@ is nil", self.delegate);
                    [self.delegateCancellations setObject:delegateCancellation forKey:cancellationKey];
                }];
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
        NSDate* date = [NSDate date];
        [self.cacheDates setObject:[NSDate date] forKey:key];
        [self.cacheKeys setObject:key forKey:[NSValue valueWithPointer:object]];
        [self.cache setObject:object forKey:key cost:self.memoryCost(object)];
        [Util executeAsync:^{
            [self threadSafeArchiveObject:object withKey:key andDate:date]; 
        }];
    }
}

- (void)removeCacheBookkeepingForObject:(id<NSCoding>)object withKey:(NSString*)key {
    if (object) {
        if (!key) {
            key = [[[self.cacheKeys objectForKey:[NSValue valueWithPointer:object]] retain] autorelease];
        }
        [self.cacheKeys removeObjectForKey:[NSValue valueWithPointer:object]];
    }
    if (key) {
        [self.cacheDates removeObjectForKey:key];
    }
}

- (void)cache:(NSCache *)cache willEvictObject:(id)obj {
    NSAssert1(obj, @"object should not have been null (%@)", obj);
    [self removeCacheBookkeepingForObject:obj withKey:nil];
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
        result = self.persistentCost;
        if (result > self.maxPersistentCost) {
            [Util executeAsync:^{
                [self shrinkPersistentStore];
            }];
        }
    }
    return result;
}

- (void)shrinkPersistentStore {
    //TODO
}

- (void)fastMemoryPurge {
    [self.cache removeAllObjects];
    [self.cacheDates removeAllObjects];
    [self.cacheKeys removeAllObjects];
}

@end
