//
//  STSharedCaches.h
//  Stamped
//
//  Created by Landon Judkins on 5/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCache.h"
#import "STStampedAPI.h"

extern NSString* const STSharedCachesDidLoadCacheNotification;

@interface STSharedCaches : NSObject

+ (STCache*)cacheForInboxScope:(STStampedAPIScope)scope;

+ (STCancellation*)cacheForInboxScope:(STStampedAPIScope)scope 
                         withCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block;

+ (STCache*)cacheForTodos;

+ (STCancellation*)cacheForTodosWithCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block;

@end
