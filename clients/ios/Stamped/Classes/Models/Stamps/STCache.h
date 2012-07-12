//
//  STCache.h
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCancellation.h"
#import "STCachePage.h"

extern NSString* const STCacheDidChangeNotification;
extern NSString* const STCacheWillLoadPageNotification;
extern NSString* const STCacheDidLoadPageNotification;

@protocol STCachePageSource <NSObject, NSCoding>

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                      withMinimumSize:(NSInteger)minimumSize
                        preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block;

@end

@protocol STCacheConfiguration <NSObject>

@required
@property (nonatomic, readonly, retain) id<STCachePageSource> pageSource;
@property (nonatomic, readonly, copy) NSURL* directory;

@optional
@property (nonatomic, readonly, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readonly, assign) NSInteger preferredPageSize;
@property (nonatomic, readonly, assign) NSInteger minimumPageSize;

@end

@protocol STCacheAccelerator <NSObject>

- (id<STDatum>)datumForCurrentDatum:(id<STDatum>)datum;

@end

@interface STCacheSnapshot : NSObject

- (id)objectAtIndex:(NSInteger)index;

@property (nonatomic, readonly, assign) NSInteger count;

@property (nonatomic, readonly, retain) STCachePage* page;

@end

@interface STCache : NSObject <STCacheConfiguration>

+ (STCancellation*)cacheForName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                  configuration:(id<STCacheConfiguration>)config
                    andCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block;

+ (STCancellation*)deleteCacheWithName:(NSString*)name 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)saveWithAccelerator:(id<STCacheAccelerator>)accel 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)ensureSavedSince:(NSDate*)date
                        accelerator:(id<STCacheAccelerator>)accel
                        andCallback:(void (^)(NSDate* date, NSError* error, STCancellation* cancellation))block;

- (void)updateObjects:(NSArray<STDatum>*)objects;

- (void)removeObjectsWithIDs:(NSSet*)doomedIDs;

- (void)updateAllWithAccellerator:(id<STCacheAccelerator>)accelerator;

- (void)clearCache;

- (STCacheSnapshot*)snapshot;
- (void)cancelPendingRequests;
- (void)refreshAtIndex:(NSInteger)index force:(BOOL)force;

- (void)dirty;

- (BOOL)hasMore;

@property (nonatomic, readwrite, retain) id<STCachePageSource> pageSource;
@property (nonatomic, readwrite, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readwrite, assign) NSInteger preferredPageSize;
@property (nonatomic, readwrite, assign) NSInteger minimumPageSize;
@property (nonatomic, readonly, copy) NSURL* directory;
@property (nonatomic, readonly, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSNumber* autoSaveAge;

@end

