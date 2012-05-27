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

@protocol STCachePageSource <NSObject, NSCoding>

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                     withMinimumSize:(NSInteger)minimumSize
                       preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block;

@end

@protocol STCacheConfiguration <NSObject>

@required
@property (nonatomic, readonly, retain) id<STCachePageSource> pageSource;

@optional
@property (nonatomic, readonly, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readonly, assign) NSInteger preferredPageSize;
@property (nonatomic, readonly, assign) NSInteger minimumPageSize;

@end

@protocol STCacheAccelerator <NSObject>

@optional
- (id<STDatum>)datumForKey:(NSString*)key
          withCurrentDatum:(id<STDatum>)datum 
                      date:(NSDate*)date 
                outputDate:(NSDate**)outputDate;

- (NSURL*)safeURLForDatumFile:(NSString*)key
             withCurrentDatum:(id<STDatum>)datum 
                         date:(NSDate*)date;

@end

@interface STCacheSnapshot : NSObject <NSCoding>

- (id)objectAtIndex:(NSInteger)index;

@property (nonatomic, readonly, assign) NSInteger count;

@end

@interface STCache : NSObject <NSCoding, STCacheConfiguration>

+ (STCancellation*)cacheForName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                  configuration:(id<STCacheConfiguration>)config
                    andCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block;

+ (STCancellation*)deleteCacheWithName:(NSString*)name 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)saveWithName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                    andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)ensureSavedSince:(NSDate*)date
                               name:(NSString*)name 
                        accelerator:(id<STCacheAccelerator>)accel
                        andCallback:(void (^)(NSDate* date, NSError* error, STCancellation* cancellation))block;

- (STCacheSnapshot*)snapshot;
- (void)cancelPendingRequests;
- (void)refreshRange:(NSRange)range;

@property (nonatomic, readwrite, retain) id<STCachePageSource> pageSource;
@property (nonatomic, readwrite, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readwrite, assign) NSInteger preferredPageSize;
@property (nonatomic, readwrite, assign) NSInteger minimumPageSize;

@end

