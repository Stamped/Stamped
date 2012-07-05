//
//  STCache.m
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCache.h"
#import "Util.h"

NSString* const STCacheDidChangeNotification = @"STCacheDidChangeNotification";
NSString* const STCacheWillLoadPageNotification = @"STCacheWillLoadPageNotification";
NSString* const STCacheDidLoadPageNotification = @"STCacheDidLoadPageNotification";

@interface STCache () <NSCoding>

- (BOOL)stale:(NSDate*)date;

@property (nonatomic, readwrite, retain) STCachePage* page;
@property (nonatomic, readonly, retain) NSMutableArray* refreshStack;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readwrite, assign) BOOL saveInProgress;

@end

@interface STCacheSnapshot ()

- (id)initWithCachePage:(STCachePage*)page;

@property (nonatomic, readonly, retain) STCachePage* page;

@end

@implementation STCache

//Public
@synthesize name = _name;
@synthesize directory = _directory;
@synthesize pageSource = _pageSource;
@synthesize pageFaultAge = _pageFaultAge;
@synthesize preferredPageSize = _preferredPageSize;
@synthesize minimumPageSize = _minimumPageSize;
@synthesize autoSaveAge = _autoSaveAge;

//Private
@synthesize page = _page;
@synthesize refreshStack = _refreshStack;
@synthesize cancellation = _cancellation;
@synthesize saveInProgress = _saveInProgress;

- (void)commonInit {
    _refreshStack = [[NSMutableArray alloc] init];
    //    _refreshSet = [[NSMutableSet alloc] init];
}

- (id)init {
    NSAssert1(NO, @"Should not use init with %@", self);
    return nil;
}

- (id)initWithName:(NSString*)name andConfiguartion:(id<STCacheConfiguration>)configuration {
    self = [super init];
    if (self) {
        _name = [name copy];
        _directory = [[configuration directory] copy];
        _pageSource = [[configuration pageSource] retain];
        _autoSaveAge = [[NSNumber numberWithInteger:3*60] retain];
        if ([configuration respondsToSelector:@selector(pageFaultAge)]) {
            _pageFaultAge = configuration.pageFaultAge;
        }
        else {
            _pageFaultAge = 1 * 24 * 60 * 60; //One day
        }
        if ([configuration respondsToSelector:@selector(preferredPageSize)]) {
            _preferredPageSize = [configuration preferredPageSize];
        }
        else {
            _preferredPageSize = 20;
        }
        if ([configuration respondsToSelector:@selector(minimumPageSize)]) {
            _minimumPageSize = [configuration minimumPageSize];
        }
        else {
            _minimumPageSize = MAX(_preferredPageSize / 2, 1);
        }
        _page = [[STCachePage alloc] initWithObjects:[NSArray array]
                                               start:[NSDate date]
                                                 end:nil 
                                             created:[NSDate dateWithTimeIntervalSinceNow:-2 * _pageFaultAge]
                                             andNext:nil];
        [self commonInit];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _name = [[decoder decodeObjectForKey:@"name"] retain];
        _directory = [[decoder decodeObjectForKey:@"directory"] retain];
        _pageSource = [[decoder decodeObjectForKey:@"pageSource"] retain];
        _pageFaultAge = [decoder decodeDoubleForKey:@"pageFaultAge"];
        _preferredPageSize = [decoder decodeIntegerForKey:@"preferredPageSize"];
        _minimumPageSize = [decoder decodeIntegerForKey:@"minimumPageSize"];
        _page = [[decoder decodeObjectForKey:@"page"] retain];
        _autoSaveAge = [[decoder decodeObjectForKey:@"autoSaveAge"] retain];
        [self commonInit];
    }
    return self;
}

- (void)dealloc
{
    [self cancelPendingRequests];
    [_name release];
    [_directory release];
    [_pageSource release];
    [_page release];
    [_refreshStack release];
    [_cancellation cancel];
    [_cancellation release];
    [_autoSaveAge release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.name forKey:@"name"];
    [encoder encodeObject:self.directory forKey:@"directory"];
    [encoder encodeObject:self.pageSource forKey:@"pageSource"];
    [encoder encodeDouble:self.pageFaultAge forKey:@"pageFaultAge"];
    [encoder encodeInteger:self.preferredPageSize forKey:@"preferredPageSize"];
    [encoder encodeInteger:self.minimumPageSize forKey:@"minimumPageSize"];
    [encoder encodeObject:self.page forKey:@"page"];
    [encoder encodeObject:self.autoSaveAge forKey:@"autoSaveAge"];
}

+ (STCancellation*)cacheForName:(NSString*)name 
                    accelerator:(id<STCacheAccelerator>)accel 
                  configuration:(id<STCacheConfiguration>)config
                    andCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeAsync:^{
        NSURL* directory = [config directory];
        NSURL* file = [directory URLByAppendingPathComponent:name];
        STCache* result = nil;
        @try {
            result = [NSKeyedUnarchiver unarchiveObjectWithFile:file.path];
        }
        @catch (NSException *exception) {
            [[NSFileManager defaultManager] removeItemAtURL:file error:nil];
        }
        @finally {
        }
        if (!result) {
            result = [[[STCache alloc] initWithName:name andConfiguartion:config] autorelease];
        }
        else {
            // NSLog(@"\n\nUnarchived Cache\n\n");
        }
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(result, nil, cancellation);
            }
        }];
    }];
    return cancellation;
}

+ (STCancellation*)deleteCacheWithName:(NSString*)name 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    //TODO
    return nil;
}

- (void)ensureDirExists {
    NSFileManager* manager = [NSFileManager defaultManager];
    if (![manager fileExistsAtPath:self.directory.path]) {
        [manager createDirectoryAtPath:self.directory.path withIntermediateDirectories:YES attributes:nil error:nil];
    }
}

- (STCancellation*)saveWithAccelerator:(id<STCacheAccelerator>)accel 
                           andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeAsync:^{
        [self ensureDirExists];
        BOOL success = NO;
        @synchronized (self) {
            NSURL* file = [self.directory URLByAppendingPathComponent:self.name];
            success = [NSKeyedArchiver archiveRootObject:self toFile:file.path];
        }
        
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(success, nil, cancellation);
            }
        }];
    }];
    return cancellation;
}

- (STCancellation*)ensureSavedSince:(NSDate*)date
                        accelerator:(id<STCacheAccelerator>)accel
                        andCallback:(void (^)(NSDate* date, NSError* error, STCancellation* cancellation))block {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeAsync:^{
        [self ensureDirExists];
        BOOL success = NO;
        NSURL* file = [self.directory URLByAppendingPathComponent:self.name];
        NSDate* currentDate = nil;
        [file getResourceValue:&currentDate forKey:NSURLCreationDateKey error:nil];
        if (!currentDate || currentDate.timeIntervalSince1970 <= date.timeIntervalSince1970) {
            @synchronized (self) {
                success = [NSKeyedArchiver archiveRootObject:self toFile:file.path];
                if (success) {
                    currentDate = [NSDate date]; 
                }
            }
        }
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(currentDate, nil, cancellation);
            }
        }];
    }];
    return cancellation;
}

- (STCacheSnapshot*)snapshot {
    return [[[STCacheSnapshot alloc] initWithCachePage:self.page] autorelease];
}

- (void)cancelPendingRequests {
    [self.cancellation cancel];
    [self.refreshStack removeAllObjects];
}

- (void)handlePage:(STCachePage*)page 
   withMinimumSize:(NSInteger)minimumSize
     preferredSize:(NSInteger)preferredSize 
  withCancellation:(STCancellation*)cancellation {
    NSAssert2(cancellation == self.cancellation, @"Unknown cancellation: %@ != %@", cancellation, self.cancellation);
    self.cancellation = nil;
    NSInteger count = self.page.count;
    if (page) {
        STCachePage* newPage = [self.page pageWithAddedPage:page];
        BOOL updated = newPage != self.page;
        self.page = newPage;
        if (updated) {
            //NSLog(@"Old count %d, new count %d", count, self.page.count);
            [[NSNotificationCenter defaultCenter] postNotificationName:STCacheDidChangeNotification object:self];
            if (self.autoSaveAge) {
                
                NSDate* date = [NSDate dateWithTimeIntervalSince1970:[[NSDate date] timeIntervalSince1970] - self.autoSaveAge.integerValue];
                [self ensureSavedSince:date accelerator:nil andCallback:^(NSDate* date, NSError* error, STCancellation* cancellation) {
                    
                }];
            }
        }
    }
    [[NSNotificationCenter defaultCenter] postNotificationName:STCacheDidLoadPageNotification object:self];
    if (count < self.page.count && self.page.count < 30) {
        [self refreshAtIndex:self.page.count force:YES];
    }
    [self continueRequests];
}

- (BOOL)hasMore {
    if (self.page.count > 0) {
        STCachePage* page = [self.page pageForIndex:self.page.count-1];
        if (page.localCount == self.minimumPageSize) { 
            return YES;
        }
        else {
            return [self stale:page.created];
        }
    }
    else {
        return [self stale:self.page.created];
    }
}

- (void)handleRefreshIndexRequest:(NSInteger)index force:(BOOL)force {
    if ([Util isOffline])
        return;
    NSDate* startDate = nil;
    STCachePage* page = nil;
    BOOL stale = NO;
    if (index < 0 || self.page.count == 0) {
        page = self.page;
        startDate = [NSDate date];
        stale = [self stale:page.created];
    }
    else if (index >= self.page.count) {
        page = [self.page pageForIndex:self.page.count-1];
        startDate = [NSDate dateWithTimeIntervalSince1970:page.end.timeIntervalSince1970 - 1];
        if (page.localCount >= self.minimumPageSize) { 
            stale = YES;
        }
        else {
            stale = [self stale:page.created];
        }
    }
    else {
        page = [self.page pageForIndex:index];
        startDate = page.start;
        stale = [self stale:page.created];
    }
    if (stale || force) {
        NSInteger minimumSize = self.minimumPageSize;
        NSInteger preferredSize = self.preferredPageSize;
        [[NSNotificationCenter defaultCenter] postNotificationName:STCacheWillLoadPageNotification object:self];
        self.cancellation = [self.pageSource pageStartingAtDate:startDate
                                                withMinimumSize:minimumSize
                                                  preferredSize:preferredSize
                                                    andCallback:^(STCachePage *page, NSError *error, STCancellation *cancellation) {
                                                        [self handlePage:page withMinimumSize:minimumSize preferredSize:preferredSize withCancellation:cancellation];
                                                    }];
    }
}

- (void)continueRequests {
    while (self.cancellation == nil && self.refreshStack.count > 0) {
        NSNumber* indexNumber = [[[self.refreshStack lastObject] retain] autorelease];
        [self.refreshStack removeLastObject];
        [self handleRefreshIndexRequest:indexNumber.integerValue force:NO];
    }
}

- (void)refreshAtIndex:(NSInteger)index force:(BOOL)force {
//    NSLog(@"refresh:%d,%d", index, force);
    NSNumber* numberIndex = [NSNumber numberWithInteger:index];
    [self.refreshStack removeObject:numberIndex];
    if (force) {
        [self.cancellation cancel];
        self.cancellation = nil;
        [self handleRefreshIndexRequest:index force:force];
    }
    else {
        [self.refreshStack addObject:numberIndex];
    }
    [self continueRequests];
}

- (BOOL)stale:(NSDate*)date {
    return [date timeIntervalSinceNow] >= self.pageFaultAge;
}

- (void)updateObjects:(NSArray<STDatum>*)objects {
    //TODO
    //for (id<STDatum> datum =in 
}

- (void)clearCache {
    self.page = [[STCachePage alloc] initWithObjects:[NSArray array]
                                   start:[NSDate date]
                                     end:nil 
                                 created:[NSDate dateWithTimeIntervalSinceNow:-2 * _pageFaultAge]
                                 andNext:nil];
    // TODO enable if possible self.saveInProgress = NO;
    [self.refreshStack removeAllObjects];
    [self.cancellation cancel];
    self.cancellation = nil;
    [self saveWithAccelerator:nil andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        
    }];
}

- (void)updateAllWithAccellerator:(id<STCacheAccelerator>)accelerator {
    STCachePage* nextPage = [self.page pageWithUpdatesFromAccelerator:accelerator];
    if (nextPage != self.page) {
        self.page = nextPage;
        [[NSNotificationCenter defaultCenter] postNotificationName:STCacheDidChangeNotification object:self];
    }
}


@end

@implementation STCacheSnapshot

@synthesize page = _page;

- (id)initWithCachePage:(STCachePage*)page {
    self = [super init];
    if (self) {
        _page = [page retain];
    }
    return self;
}

- (void)dealloc
{
    [_page release];
    [super dealloc];
}

- (id)objectAtIndex:(NSInteger)index {
    NSAssert2(index < self.count, @"Index is beyond count: %d, %d", index, self.count);
    return [_page objectAtIndex:index];
}

- (NSInteger)count {
    return _page.count;
}

@end
