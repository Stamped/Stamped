//
//  STSpotify.h
//  Stamped
//
//  Created by Landon Judkins on 6/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCancellation.h"
#import "STActionDelegate.h"

extern NSString* const STSpotifyTrackEndedNotification;

@interface STSpotify : NSObject <STActionDelegate>

+ (STSpotify*)sharedInstance;

- (BOOL)connected;

- (STCancellation*)loginWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)logoutWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (void)addToPlaylistWithTrackURI:(NSString*)trackURI;

@property (nonatomic, readonly, assign) BOOL loggedIn;

@end
