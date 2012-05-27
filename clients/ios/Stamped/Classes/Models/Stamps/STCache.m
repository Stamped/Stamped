//
//  STCache.m
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCache.h"


@interface STCache : NSObject <NSCoding, STCacheConfiguration>

- (void)cancelPendingRequests;
- (void)refreshRange:(NSRange)range;

@property (nonatomic, readwrite, retain) id<STCachePageSource> pageSource;
@property (nonatomic, readwrite, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readwrite, assign) NSInteger preferredPageSize;
@property (nonatomic, readwrite, assign) NSInteger minimumPageSize;
@interface STCache ()

- (STCachePage*)firstPage;

- (void)processPage:(STCachePage*)page;

- (STCancellation*)pageForDate:(NSDate*)date 
              withMinimumCount:(NSInteger)minimumCount 
                   andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readwrite, retain) NSString* firstKey;
@property (nonatomic, readwrite, retain) NSString* lastKey;
@property (nonatomic, readonly, retain) NSMutableDictionary* pageForKey;
@property (nonatomic, readwrite, retain) NSMutableDictionary* cancellationsByTriggerDate;
//TODO minimum page size
//@property (nonatomic, readwrite, assign) NSInteger minimumPageSize;

@end

@implementation STCache

//Public
@synthesize pageFaultAge = _pageFaultAge;

//Private
@synthesize firstKey = _firstKey;
@synthesize lastKey = _lastKey;
@synthesize pageForKey = _pageForKey;
@synthesize cancellationsByTriggerDate = _cancellationsByTriggerDate;



- (id)init {
    self = [super init];
    if (self) {
        _pageForKey = [[NSMutableDictionary alloc] init];
        _pageFaultAge = 1 * 24 * 60 * 60; //One day
        _cancellationsByTriggerDate = [[NSMutableDictionary alloc] init];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _pageFaultAge = [decoder decodeDoubleForKey:@"pageFaultAge"];
        _pageForKey = [decoder decodeObjectForKey:@"pageForKey"];
        _firstKey = [decoder decodeObjectForKey:@"firstKey"];
        _lastKey = [decoder decodeObjectForKey:@"lastKey"];
        _cancellationsByTriggerDate = [[NSMutableDictionary alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [self cancelPendingRequests];
    [_pageForKey release];
    [_lastKey release];
    [_pageForKey release];
    [_cancellationsByTriggerDate release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeDouble:self.pageFaultAge forKey:@"pageFaultAge"];
    [encoder encodeObject:self.firstKey forKey:@"firstKey"];
    [encoder encodeObject:self.lastKey forKey:@"lastKey"];
    [encoder encodeObject:self.pageForKey forKey:@"pageForKey"];
}


+ (STCancellation*)cacheForName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                  configuration:(id<STCacheConfiguration>)config
                    andCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block {
    
}

+ (STCancellation*)deleteCacheWithName:(NSString*)name 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    
}

- (STCancellation*)saveWithName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                    andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    
}

- (STCancellation*)ensureSavedSince:(NSDate*)date
name:(NSString*)name 
accelerator:(id<STCacheAccelerator>)accel
                        andCallback:(void (^)(NSDate* date, NSError* error, STCancellation* cancellation))block {
    
}

- (STCacheSnapshot*)snapshot {
    
}

- (STCachePage*)pageContainingDate:(NSDate*)date {
    STCachePage* lastPage = nil;
    STCachePage* curPage = self.firstPage;
    while (curPage) {
        if ([date compare:curPage.mostRecentDate] == NSOrderedAscending) {
            //page starts after date
            break;
        }
        else {
            //page starts before or equal to date
            lastPage = curPage;
            curPage = curPage.next;
        }
    }
    NSAssert2(lastPage == nil || [date compare:lastPage.mostRecentDate] == NSOrderedAscending, @"Expected page to start (%@) before date (%@)", lastPage.mostRecentDate, date);
    return lastPage;
}

- (id)objectAtIndex:(NSInteger)index {
    NSInteger offset = index;
    STCachePage* page = self.firstPage;
    while (offset > page.count) {
        offset -= page.count;
        page = page.next;
    }
    NSDate* pageDate = page.timestamp;
    if ([pageDate timeIntervalSinceNow] > self.pageFaultAge && ![self.cancellationsByTriggerDate objectForKey:pageDate]) {
        //TODO address segmentation
        //TODO consider __block reference instead
        STCancellation* cancellation = [self pageForDate:pageDate withMinimumCount:20 andCallback:^(STCachePage *page, NSError *error, STCancellation *cancellation) {
            [self.cancellationsByTriggerDate removeObjectForKey:pageDate];
            if (page) {
                [self processPage:page];
            }
        }];
        [self.cancellationsByTriggerDate setObject:cancellation forKey:pageDate];
    }
    return [page objectAtIndex:offset];
}

- (void)cancelPendingRequests {
    for (STCancellation* canellation in [_cancellationsByTriggerDate allValues]) {
        [canellation cancel];
    }
    [_cancellationsByTriggerDate removeAllObjects];
}

- (void)processPage:(STCachePage *)page {
    if (self.firstPage == nil) {
        
    }
    else {
        
    }
    STCachePage* prev = [self pageContainingDate:page.mostRecentDate];
    STCachePage* next = prev.next;
    NSAssert1(prev.count > 0, @"Expected page to be non empty in %@", self);
    NSArray* removedFromPrev = [prev objectsBeforeOrOnDate:page.mostRecentDate];
    for (id<STDatum> datum in removedFromPrev) {
        [self.pageForKey removeObjectForKey:datum.key];
        [prev removeObjectWithKey:datum.key];
    }
    if (
    for (NSInteger i = prev.count - prevRemoveCount; i < prev.count; i++) {
        id object = [prev objectAtIndex:i];
        
    }
}

@end
