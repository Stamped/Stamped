//
//  STCreditPageSource.m
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCreditPageSource.h"
#import "STStampedAPI.h"

@interface STCreditPageSource ()

@property (nonatomic, readonly, copy) NSString* userID;

@end

@implementation STCreditPageSource

@synthesize userID = _userID;

- (id)initWithUserID:(NSString*)userID {
    self = [super init];
    if (self) {
        _userID = [userID retain];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
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
    [encoder encodeObject:self.userID forKey:@"userID"];
}

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                      withMinimumSize:(NSInteger)minimumSize
                        preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block {
    return [[STStampedAPI sharedInstance] creditingStampsWithUserID:self.userID 
                                                               date:date 
                                                              limit:minimumSize 
                                                             offset:0
                                                        andCallback:^(NSArray<STStamp> *stamps, NSError *error, STCancellation *cancellation) {
                                                            if (stamps) {
                                                                STCachePage* page = [[[STCachePage alloc] initWithObjects:stamps start:date end:nil created:nil andNext:nil] autorelease];
                                                                block(page, nil, cancellation);
                                                            }
                                                            else {
                                                                block(nil, error, cancellation);
                                                            }
                                                        }];
}

@end
