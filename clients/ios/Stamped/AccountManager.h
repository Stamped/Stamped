//
//  AccountManager.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "User.h"
#import "OAuthToken.h"
#import "FirstRunViewController.h"

extern NSString* const kCurrentUserHasUpdatedNotification;
extern NSString* const kUserHasLoggedOutNotification;
// too many warnings #warning Switched to iphone8@2x id
static NSString* const kClientID = @"iphone8@2x";
static NSString* const kClientSecret = @"LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu";
//static NSString* const kClientID = @"stampedtest";
//static NSString* const kClientSecret = @"august1ftw";

@protocol AccountManagerDelegate
@required
- (void)accountManagerDidAuthenticate;
@end

@class KeychainItemWrapper;

@interface AccountManager : NSObject<RKObjectLoaderDelegate, RKRequestQueueDelegate, FirstRunViewControllerDelegate> {
 @private
  KeychainItemWrapper* passwordKeychainItem_;
  KeychainItemWrapper* accessTokenKeychainItem_;
  KeychainItemWrapper* refreshTokenKeychainItem_;
  RKRequestQueue* oAuthRequestQueue_;
  NSTimer* oauthRefreshTimer_;
  BOOL coldLaunch_;
  BOOL firstInstall_;
}

+ (AccountManager*)sharedManager;
- (void)authenticate;
- (void)refreshToken;
- (void)logout;

@property (nonatomic, retain) User* currentUser;
@property (nonatomic, retain) OAuthToken* authToken;
@property (nonatomic, assign) id<AccountManagerDelegate> delegate;
@property (nonatomic, readonly) BOOL authenticated;


- (void)createAccountWithFacebook:(NSString*)name
                       screenname:(NSString*)screenname
                        userToken:(NSString*)userToken 
                            email:(NSString*)email;
@end
