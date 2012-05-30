//
//  STSharedCaches.m
//  Stamped
//
//  Created by Landon Judkins on 5/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSharedCaches.h"
#import "STInboxPageSource.h"
#import "STGenericCacheConfiguration.h"
#import "Util.h"

NSString* const STSharedCachesDidLoadCacheNotification = @"STSharedCachesDidLoadCacheNotification";

@implementation STSharedCaches

static STCache* _inboxYou = nil;
static STCache* _inboxInbox = nil;
static STCache* _inboxFriendsOfFriends = nil;
static STCache* _inboxEveryone = nil;

+ (STCache*)cacheForInboxScope:(STStampedAPIScope)scope {
    switch (scope) {
        case STStampedAPIScopeYou:
            return _inboxYou;
        case STStampedAPIScopeFriends:
            return _inboxInbox;
        case STStampedAPIScopeFriendsOfFriends:
            return _inboxFriendsOfFriends;
        case STStampedAPIScopeEveryone:
            return _inboxEveryone;
        default:
            return nil;
    }
}

+ (STCancellation*)cacheForInboxScope:(STStampedAPIScope)scope 
                         withCallback:(void (^)(STCache* cache, NSError* error, STCancellation* cancellation))block {
    STCache* fastCache = [self cacheForInboxScope:scope];
    if (fastCache) {
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(fastCache, nil, cancellation);
            }
        }];
        return cancellation;
    }
    else {
        id<STCachePageSource> pageSource = [[[STInboxPageSource alloc] initWithScope:scope] autorelease];
        STGenericCacheConfiguration* configuration = [[STGenericCacheConfiguration alloc] init];
        configuration.pageSource = pageSource;
        NSString* name = [NSString stringWithFormat:@"InboxCache%@", [[STStampedAPI sharedInstance] stringForScope:scope]];
        return [STCache cacheForName:name
                  accelerator:nil
                configuration:configuration
                  andCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
                      STCache** dst = nil;
                      switch (scope) {
                          case STStampedAPIScopeYou:
                              dst = &_inboxYou;
                              break;
                          case STStampedAPIScopeFriends:
                              dst = &_inboxInbox;
                              break;
                          case STStampedAPIScopeFriendsOfFriends:
                              dst = &_inboxFriendsOfFriends;
                              break;
                          case STStampedAPIScopeEveryone:
                              dst = &_inboxEveryone;
                              break;
                          default:
                              NSAssert1(NO, @"Unknown scope: %d", scope);
                      }
                      if (cache && dst && !*dst) {
                          *dst = [cache retain];
                      }
                      block(cache, error, cancellation);
                  }];
    }
}

@end
