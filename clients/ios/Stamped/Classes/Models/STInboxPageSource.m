//
//  STInboxPageSource.m
//  Stamped
//
//  Created by Landon Judkins on 5/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxPageSource.h"
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"

@interface STInboxPageSource ()

@property (nonatomic, readonly, assign) STStampedAPIScope scope;
@property (nonatomic, readonly, copy) NSString* userID;

@end

@implementation STInboxPageSource

@synthesize scope = _scope;
@synthesize userID = _userID;

- (id)init {
    NSAssert1(NO, @"Don't use init() with %@", self);
    return nil;
}

- (id)initWithScope:(STStampedAPIScope)scope {
    self = [super init];
    if (self) {
        _scope = scope;
    }
    return self;
}

- (id)initWithUserID:(NSString*)userID {
    self = [super init];
    if (self) {
        _userID = [userID copy];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _scope = [decoder decodeIntegerForKey:@"scope"];
        _userID = [[decoder decodeObjectForKey:@"userID"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_userID release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [encoder encodeInteger:self.scope forKey:@"scope"];
    [encoder encodeObject:self.userID forKey:@"userID"];
}

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                      withMinimumSize:(NSInteger)minimumSize
                        preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block {
    if (self.userID) {
        return [[STStampedAPI sharedInstance] stampsWithUserID:self.userID date:date limit:minimumSize offset:0 andCallback:^(NSArray<STStamp> *stamps, NSError *error, STCancellation *cancellation) {
            if (stamps) {
                //TODO handle multiple stamps at a specific time
                STCachePage* page = [[[STCachePage alloc] initWithObjects:stamps start:date end:nil created:nil andNext:nil] autorelease];
                block(page, nil, cancellation);
            }
            else {
                block(nil, error, cancellation);
            }
        }];
    }
    else {
        if ([STStampedAPI sharedInstance].currentUser == nil && self.scope != STStampedAPIScopeEveryone) {
            STCancellation* cancellation = [STCancellation cancellation];
            [Util executeOnMainThread:^{
                if (!cancellation.cancelled) {
                    block(nil, [NSError errorWithDomain:@"stamped.no_user" code:0 userInfo:nil], cancellation);
                }
            }];
            return cancellation;
        }
        return [[STStampedAPI sharedInstance] stampsWithScope:self.scope date:date limit:minimumSize offset:0 andCallback:^(NSArray<STStamp> *stamps, NSError *error, STCancellation *cancellation) {
            if (stamps) {
                //TODO handle multiple stamps at a specific time
                STCachePage* page = [[[STCachePage alloc] initWithObjects:stamps start:date end:nil created:nil andNext:nil] autorelease];
                block(page, nil, cancellation);
            }
            else {
                block(nil, error, cancellation);
            }
        }];
    }
}

@end
