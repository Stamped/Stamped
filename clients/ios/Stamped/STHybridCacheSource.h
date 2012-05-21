//
//  STHybridCacheSource.h
//  Stamped
//
//  Created by Landon Judkins on 5/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STModelSource.h"

@class STHybridCacheSource;

@protocol STHybridCacheSourceDelegate <NSObject>
@required
- (STCancellation*)objectForHybridCache:(STHybridCacheSource*)cache 
                                withKey:(NSString*)key
                           withCallback:(void(^)(id<NSCoding> model, NSError* error, STCancellation* cancellation))block;
@end

@interface STHybridCacheSource : NSObject

@property (nonatomic, readwrite, assign) id<STHybridCacheSourceDelegate> delegate;
@property (nonatomic, readwrite, assign) NSInteger maxMemoryCount;
@property (nonatomic, readwrite, assign) NSInteger maxPersistentCost;
@property (nonatomic, readwrite, copy) NSNumber* maxAge;

- (id)initWithCachePath:(NSString*)path relativeToCacheDir:(BOOL)relative;

- (id<NSCoding>)fastCachedObjectForKey:(NSString*)key;

- (id<NSCoding>)cachedObjectForKey:(NSString*)key;

- (STCancellation*)objectForKey:(NSString*)key 
                    forceUpdate:(BOOL)update 
                   withCallback:(void (^)(id<NSCoding> model, NSError* error, STCancellation* cancellation))block;

- (void)removeObjectForKey:(NSString*)key;

- (void)setObject:(id<NSCoding>)object forKey:(NSString*)key;

- (void)fastMemoryPurge;

@end
