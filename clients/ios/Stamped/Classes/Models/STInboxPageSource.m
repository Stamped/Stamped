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

@end

@implementation STInboxPageSource

@synthesize scope = _scope;

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

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _scope = [decoder decodeIntegerForKey:@"scope"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [encoder encodeInteger:self.scope forKey:@"scope"];
}

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                      withMinimumSize:(NSInteger)minimumSize
                        preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block {
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

@end
