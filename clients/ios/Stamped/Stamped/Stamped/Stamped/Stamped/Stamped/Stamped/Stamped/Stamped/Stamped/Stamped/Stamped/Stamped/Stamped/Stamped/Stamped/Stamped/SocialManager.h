//
//  SocialManager.h
//  Stamped
//
//  Created by Jake Zien on 11/14/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

/*
 TODO - Consider relationship with Third Party group
 */

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "FBConnect.h"

@class Stamp;
@class FacebookUser;
@class TwitterUser;

extern NSString* const kSocialNetworksChangedNotification;
extern NSString* const kTwitterFriendsChangedNotification;
extern NSString* const kTwitterFriendsNotOnStampedReceivedNotification;
extern NSString* const kFacebookFriendsChangedNotification;
extern NSString* const kStampedFindFacebookFriendsPath;
extern NSString* const kStampedFindTwitterFriendsPath;

@interface SocialManager : NSObject <RKObjectLoaderDelegate,
                                     RKRequestDelegate,
                                     FBSessionDelegate,
                                     FBRequestDelegate,
                                     UIActionSheetDelegate,
                                     UIAlertViewDelegate>

+ (SocialManager*)sharedManager;
- (BOOL)hasiOS5Twitter;
- (void)signInToTwitter:(UINavigationController*)navigationController;
- (void)signInToFacebook;
- (void)signOutOfTwitter:(BOOL)unlink;
- (void)signOutOfFacebook:(BOOL)unlink;
- (BOOL)isSignedInToTwitter;
- (BOOL)isSignedInToFacebook;
- (void)requestFacebookPostWithStamp:(Stamp*)stamp;
- (void)requestFacebookPostInviteToFacebookID:(NSString*)facebookID;
- (void)requestTwitterPostWithStamp:(Stamp*)stamp;
- (void)requestTwitterPostWithStatus:(NSString*)status;
- (void)refreshStampedFriendsFromFacebook;
- (void)refreshStampedFriendsFromTwitter;
- (BOOL)handleOpenURLFromFacebook:(NSURL*)URL;

// TODO(andybons): This should be readonly, not retain.
@property (nonatomic, retain) NSMutableSet* twitterFriendsNotUsingStamped;
@property (nonatomic, retain) NSMutableSet* facebookFriendsNotUsingStamped;

@property (nonatomic, readonly) NSString* stampedLogoImageURL;
@property (nonatomic, readonly) NSString* facebookName;
@property (nonatomic, readonly) NSString* facebookProfileImageURL;
@property (nonatomic, readonly) NSString* twitterUsername;
@property (nonatomic, readonly) NSString* twitterProfileImageURL;
@property (nonatomic, readonly) NSString* largeTwitterProfileImageURL;


@end
