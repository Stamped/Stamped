//
//  SocialManager.h
//  Stamped
//
//  Created by Jake Zien on 11/14/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "FBConnect.h"

@class Stamp;

extern NSString* const kSocialNetworksChangedNotification;
extern NSString* const kTwitterFriendsChangedNotification;
extern NSString* const kFacebookFriendsChangedNotification;
extern NSString* const kStampedFindFacebookFriendsPath;
extern NSString* const kStampedFindTwitterFriendsPath;

@interface SocialManager : NSObject <RKObjectLoaderDelegate,
                                     RKRequestDelegate,
                                     FBSessionDelegate,
                                     FBRequestDelegate,
                                     UIActionSheetDelegate>

+ (SocialManager*)sharedManager;
- (BOOL)hasiOS5Twitter;
- (void)signInToTwitter:(UINavigationController*)navigationController;
- (void)signInToFacebook;
- (void)signOutOfTwitter:(BOOL)unlink;
- (void)signOutOfFacebook:(BOOL)unlink;
- (BOOL)isSignedInToTwitter;
- (BOOL)isSignedInToFacebook;
- (void)requestFacebookPostWithStamp:(Stamp*)stamp;
- (void)requestTwitterPostWithStamp:(Stamp*)stamp;
- (void)refreshStampedFriendsFromFacebook;
- (void)refreshStampedFriendsFromTwitter;
- (BOOL)handleOpenURLFromFacebook:(NSURL*)URL;

@end
