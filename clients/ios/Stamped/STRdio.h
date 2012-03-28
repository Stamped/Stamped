//
//  STRdio.h
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STViewDelegate.h"

@interface STRdio : NSObject <STViewDelegate>

+ (STRdio*)sharedRdio;

- (void)ensureLoginWithCompletionBlock:(void(^)(void))block;
- (void)startPlayback:(NSString*)rdioID;

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action;
- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action;

@property (nonatomic, readonly, assign) BOOL loggedIn;
@property (nonatomic, readonly, copy) NSString* accessToken;

@end
