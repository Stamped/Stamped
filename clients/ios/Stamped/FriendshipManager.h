//
//  FriendshipManager.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/8/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>

@class User;

@interface FriendshipManager : NSObject <RKObjectLoaderDelegate>

+ (FriendshipManager*)sharedManager;

- (void)followUser:(User*)user;
- (void)unfollowUser:(User*)user;

@end
