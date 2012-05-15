//
//  STUserImageCache.m
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STImageCache.h"
#import "STCacheModelSource.h"
#import "Util.h"
#import "STURLConnection.h"

@interface STImageCache () <STCacheModelSourceDelegate>

@property (nonatomic, readonly, retain) STCacheModelSource* cache;

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
    cache_ = [[STCacheModelSource alloc] initWithDelegate:self];
    cache_.maximumCost = 10 * 1000 * 1000; // 10 megs
  }
  return self;
}

- (void)dealloc
{
  [cache_ release];
  [super dealloc];
}

- (STCancellation*)objectForCache:(STCacheModelSource*)cache 
                          withKey:(NSString*)key 
                 andCurrentObject:(id)object 
                     withCallback:(void(^)(id, NSInteger, NSError*, STCancellation*))block {
  STCancellation* cancellation = [STURLConnection cancellationWithURL:[NSURL URLWithString:key] 
                                                          andCallback:^(NSData *data, NSError *error, STCancellation *cancellation2) {
                                                            if (data) {
                                                              UIImage* image = [UIImage imageWithData:data];
                                                              block(image, data.length, nil, cancellation2);
                                                            }
                                                            else {
                                                              block(nil, -1, error, cancellation2);
                                                            }
                                                          }];
  return cancellation;
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
  STCancellation* cancellation = [STCancellation cancellation];
  [self.cache fetchWithKey:URL callback:^(id model, NSError *error, STCancellation* cancellation2) {
    if (!cancellation.cancelled) {
      block(model, error, cancellation);
    }
  }];
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
  return [self.cache cachedValueForKey:URL];
}

- (void)fastPurge {
  [self.cache fastPurge];
}

@end
