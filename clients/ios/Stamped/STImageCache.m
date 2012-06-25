//
//  STUserImageCache.m
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STImageCache.h"
#import "Util.h"
#import "STURLConnection.h"
#import "STHybridCacheSource.h"

@interface STImageCache () <STHybridCacheSourceDelegate>

@property (nonatomic, readonly, retain) STHybridCacheSource* cache;

@end

@implementation STImageCache

@synthesize cache = cache_;

static STImageCache* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STImageCache alloc] init];
}

+ (STImageCache*)sharedInstance {
    return _sharedInstance;
}

- (id)init
{
    self = [super init];
    if (self) {
        cache_ = [[STHybridCacheSource alloc] initWithCachePath:@"com.stamped.Images" relativeToCacheDir:YES];
        cache_.maxMemoryCost = 400;
        cache_.delegate = self;
    }
    return self;
}

- (void)dealloc
{
    [cache_ release];
    [super dealloc];
}

- (void)cacheImage:(UIImage*)image forImageURL:(NSString*)url {
    [self.cache setObject:image forKey:url];
}

- (STCancellation *)objectForHybridCache:(STHybridCacheSource *)cache
                                 withKey:(NSString *)key 
                            withCallback:(void (^)(id<NSCoding>, NSError *, STCancellation *))block {
    return [STURLConnection cancellationWithURL:[NSURL URLWithString:key]
                                    andCallback:^(NSData *data, NSError *error, STCancellation *cancellation) {
                                        if (data) {
                                            UIImage* image = [UIImage imageWithData:data];
                                            block(image, nil, cancellation);
                                        }
                                        else {
                                            block(nil, error, cancellation);
                                        }
                                    }];
}

- (STCancellation*)userImageForUser:(id<STUser>)user 
                               size:(STProfileImageSize)size
                        andCallback:(void(^)(UIImage*, NSError*, STCancellation*))block {
    NSString* url = [Util profileImageURLForUser:user withSize:size];
    return [self imageForImageURL:url andCallback:block];
}

- (STCancellation*)entityImageForEntityDetail:(id<STEntityDetail>)entityDetail
                                  andCallback:(void(^)(UIImage* image, NSError* error, STCancellation* cancellation))block {
    NSString* url = [Util entityImageURLForEntityDetail:entityDetail];
    return [self imageForImageURL:url andCallback:block];
}

- (STCancellation*)imageForImageURL:(NSString*)URL
                        andCallback:(void(^)(UIImage* image, NSError* error, STCancellation* cancellation))block {
    NSAssert(URL != nil, @"Requested nil URL");
    STCancellation* cancellation = [STCancellation cancellation];
    [self.cache objectForKey:URL forceUpdate:YES cacheAfterCancel:YES withCallback:^(id<NSCoding> model, NSError *error, STCancellation *cancellation) {
        if (!cancellation.cancelled) {
            block((UIImage*)model, error, cancellation);
        }
    }];;
    return cancellation;
}

- (UIImage*)cachedUserImageForUser:(id<STUser>)user 
                              size:(STProfileImageSize)size {
    return [self cachedImageForImageURL:[Util profileImageURLForUser:user withSize:size]];
}

- (UIImage*)cachedEntityImageForEntityDetail:(id<STEntityDetail>)entityDetail {
    return [self cachedImageForImageURL:[Util entityImageURLForEntityDetail:entityDetail]];
}

- (UIImage*)cachedImageForImageURL:(NSString*)URL {
    NSAssert(URL != nil, @"Requested nil URL");
    return (UIImage*)[self.cache fastCachedObjectForKey:URL];
}

- (void)fastPurge {
    [self.cache fastMemoryPurge];
}

@end
