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

extern NSString* const kCurrentUserHasUpdatedNotification;

@protocol AccountManagerDelegate
@required
- (void)accountManagerDidAuthenticate;
@end

@class KeychainItemWrapper;

@interface AccountManager : NSObject<RKObjectLoaderDelegate, RKRequestQueueDelegate, UIAlertViewDelegate> {
 @private
  KeychainItemWrapper* passwordKeychainItem_;
  KeychainItemWrapper* accessTokenKeychainItem_;
  KeychainItemWrapper* refreshTokenKeychainItem_;
  RKRequestQueue* oAuthRequestQueue_;
  UITextField* usernameField_;
  UITextField* passwordField_;
  NSTimer* oauthRefreshTimer_;
  BOOL firstRun_;
}

+ (AccountManager*)sharedManager;
- (void)authenticate;
- (void)refreshToken;

@property (nonatomic, retain) UIAlertView* alertView; 
@property (nonatomic, retain) User* currentUser;
@property (nonatomic, retain) OAuthToken* authToken;
@property (nonatomic, assign) id<AccountManagerDelegate> delegate;
@property (nonatomic, readonly) BOOL authenticated;

@end
