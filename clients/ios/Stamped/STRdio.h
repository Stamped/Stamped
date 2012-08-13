//
//  STRdio.h
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActionDelegate.h"
#import <Rdio/Rdio.h>

@interface STRdio : NSObject <STActionDelegate>

+ (STRdio*)sharedRdio;

- (void)ensureLoginWithCompletionBlock:(void(^)(void))block;
- (void)startPlayback:(NSString*)rdioID __attribute__ ((deprecated));
- (void)stopPlayback __attribute__ ((deprecated));

- (void)logout;

@property (nonatomic, readonly, retain) Rdio* rdio;
@property (nonatomic, readonly, assign) BOOL loggedIn;
@property (nonatomic, readonly, assign) BOOL connected;
@property (nonatomic, readonly, copy) NSString* accessToken;

@end
