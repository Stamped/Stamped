//
//  AccountManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "AccountManager.h"

#import <RestKit/CoreData/CoreData.h>

#import "KeychainItemWrapper.h"
#import "OAuthToken.h"

static NSString* const kPasswordKeychainItemID = @"Password";
static NSString* const kAccessTokenKeychainItemID = @"AccessToken";
static NSString* const kRefreshTokenKeychainItemID = @"RefreshToken";
static NSString* const kClientID = @"stampedtest";
static NSString* const kClientSecret = @"august1ftw";
static NSString* const kLoginPath = @"/oauth2/login.json";
static NSString* const kRefreshPath = @"/oauth2/token.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";
static NSString* const kTokenExpirationUserDefaultsKey = @"TokenExpirationDate";
static const NSUInteger kMaxAuthRetries = 3;
static AccountManager* sharedAccountManager_ = nil;

@interface AccountManager ()
- (void)sendLoginRequest;
- (void)sendTokenRefreshRequest;
- (void)sendUserInfoRequest;
- (void)showAuthAlert;
- (void)refreshTimerFired:(NSTimer*)theTimer;
@end

@implementation AccountManager

@synthesize authToken = authToken_;
@synthesize currentUser = currentUser_;
@synthesize delegate = delegate_;
@synthesize alertView = alertView_;

+ (AccountManager*)sharedManager {
  if (sharedAccountManager_ == nil)
    sharedAccountManager_ = [[super allocWithZone:NULL] init];

  return sharedAccountManager_;
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedManager] retain];
}

- (id)copyWithZone:(NSZone*)zone {
  return self;
}

- (id)retain {
  return self;
}

- (NSUInteger)retainCount {
  return NSUIntegerMax;
}

- (oneway void)release {
  // Do nothin'.
}

- (id)autorelease {
  return self;
}

#pragma mark - Begin custom implementation.

- (id)init {
  self = [super init];
  if (self) {
    firstRun_ = YES;
    passwordKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kPasswordKeychainItemID];
    accessTokenKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kAccessTokenKeychainItemID];
    refreshTokenKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kRefreshTokenKeychainItemID];
  }
  return self;
}

- (void)refreshToken {
  [self sendTokenRefreshRequest];
}

- (void)showAuthAlert {
  UIAlertView* alertView = [[UIAlertView alloc] initWithTitle:nil
                                                     message:@"\n\n\n"
                                                    delegate:self
                                           cancelButtonTitle:@"Cancel"
                                           otherButtonTitles:@"Go", nil];
  usernameField_ = [[UITextField alloc] initWithFrame:CGRectMake(16, 20, 252, 25)];
  usernameField_.placeholder = @"username";
  usernameField_.borderStyle = UITextBorderStyleRoundedRect;
  usernameField_.autocapitalizationType = UITextAutocapitalizationTypeNone;
  usernameField_.autocorrectionType = UITextAutocorrectionTypeNo;
  usernameField_.keyboardAppearance = UIKeyboardAppearanceAlert;
  [usernameField_ becomeFirstResponder];
  [alertView addSubview:usernameField_];
  [usernameField_ release];
  passwordField_ = [[UITextField alloc] initWithFrame:CGRectMake(16, 55, 252, 25)];
  passwordField_.placeholder = @"password";
  passwordField_.secureTextEntry = YES;
  passwordField_.borderStyle = UITextBorderStyleRoundedRect;
  passwordField_.autocapitalizationType = UITextAutocapitalizationTypeNone;
  passwordField_.autocorrectionType = UITextAutocorrectionTypeNo;
  passwordField_.keyboardAppearance = UIKeyboardAppearanceAlert;
  [alertView addSubview:passwordField_];
  [passwordField_ release];
  alertView.delegate = self;
  [alertView show];
  self.alertView = alertView;
  [alertView release];
}

- (void)authenticate {
  NSString* userID = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  if (userID.length > 0) {
    self.currentUser = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"userID == %@", userID]];
  } else {
    [self showAuthAlert];
    return;
  }
  NSString* accessToken = [accessTokenKeychainItem_ objectForKey:(id)kSecValueData];
  NSString* refreshToken = [refreshTokenKeychainItem_ objectForKey:(id)kSecValueData];
  if (!(accessToken && refreshToken)) {
    [self sendLoginRequest];
    return;
  }
  if (firstRun_) {
    self.authToken = [[[OAuthToken alloc] init] autorelease];
    self.authToken.accessToken = accessToken;
    self.authToken.refreshToken = refreshToken;
    NSDate* tokenExpirationDate = [[NSUserDefaults standardUserDefaults] objectForKey:kTokenExpirationUserDefaultsKey];
    NSTimeInterval timeUntilTokenRefresh = [tokenExpirationDate timeIntervalSinceNow];
    if (timeUntilTokenRefresh <= 0) {
      [self sendTokenRefreshRequest];
      return;
    }
    oauthRefreshTimer_ = [NSTimer scheduledTimerWithTimeInterval:timeUntilTokenRefresh
                                                          target:self
                                                        selector:@selector(refreshTimerFired:)
                                                        userInfo:nil
                                                         repeats:YES];
    [self sendUserInfoRequest];
    [self.delegate accountManagerDidAuthenticate];
    firstRun_ = NO;
  }
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.resourcePath isEqualToString:kLoginPath]) {
    if (![objectLoader.response isUnauthorized] && numRetries_++ < kMaxAuthRetries) {
      [self sendLoginRequest];
      return;
    }
    [self showAuthAlert];
    return;
  } else if ([objectLoader.resourcePath isEqualToString:kRefreshPath]) {
    [self sendLoginRequest];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  numRetries_ = 0;

  if ([object isKindOfClass:[User class]]) {
    self.currentUser = (User*)object;
    return;
  }
  
  OAuthToken* token = object;
  if ([objectLoader.resourcePath isEqualToString:kLoginPath]) {
    [refreshTokenKeychainItem_ setObject:@"RefreshToken" forKey:(id)kSecAttrAccount];
    [refreshTokenKeychainItem_ setObject:token.refreshToken forKey:(id)kSecValueData];
    self.authToken = token;
  }
  [refreshTokenKeychainItem_ setObject:@"AccessToken" forKey:(id)kSecAttrAccount];
  [accessTokenKeychainItem_ setObject:token.accessToken forKey:(id)kSecValueData];
  self.authToken.accessToken = token.accessToken;

  [[NSUserDefaults standardUserDefaults] setObject:[NSDate dateWithTimeIntervalSinceNow:token.lifetimeSecs]
                                            forKey:kTokenExpirationUserDefaultsKey];
  [[NSUserDefaults standardUserDefaults] synchronize];
  
  if (oauthRefreshTimer_) {
    [oauthRefreshTimer_ invalidate];
    oauthRefreshTimer_ = nil;
  }
  oauthRefreshTimer_ = [NSTimer scheduledTimerWithTimeInterval:token.lifetimeSecs
                                                        target:self
                                                      selector:@selector(refreshTimerFired:)
                                                      userInfo:nil
                                                       repeats:YES];
  if (firstRun_) {
    [self.delegate accountManagerDidAuthenticate];
    firstRun_ = NO;
  }

  [self sendUserInfoRequest];
}

- (void)sendLoginRequest {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* oauthMapping = [objectManager.mappingProvider mappingForKeyPath:@"OAuthToken"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kLoginPath
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = oauthMapping;
  NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  NSString* password = [passwordKeychainItem_ objectForKey:(id)kSecValueData];
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      username, @"screen_name",
      password, @"password",
      kClientID, @"client_id",
      kClientSecret, @"client_secret", nil];
  [objectLoader send];
}

- (void)sendTokenRefreshRequest {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* oauthMapping = [objectManager.mappingProvider mappingForKeyPath:@"OAuthToken"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kRefreshPath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = oauthMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
                         [refreshTokenKeychainItem_ objectForKey:(id)kSecValueData], @"refresh_token",
                         @"refresh_token", @"grant_type",
                         kClientID, @"client_id",
                         kClientSecret, @"client_secret", nil];
  [objectLoader send];
}

- (void)sendUserInfoRequest {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  NSDictionary* params =
      [NSDictionary dictionaryWithKeysAndObjects:@"screen_names", username,
                                                 @"oauth_token", self.authToken.accessToken,
                                                 nil];
  [objectManager loadObjectsAtResourcePath:[kUserLookupPath appendQueryParams:params]
                             objectMapping:userMapping
                                  delegate:self];
}

- (void)refreshTimerFired:(NSTimer*)theTimer {
  [self sendTokenRefreshRequest];
}

#pragma mark - UIAlertViewDelegate methods.

- (void)alertView:(UIAlertView*)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
  [passwordKeychainItem_ setObject:usernameField_.text forKey:(id)kSecAttrAccount];
  [passwordKeychainItem_ setObject:passwordField_.text forKey:(id)kSecValueData];
  usernameField_ = nil;
  passwordField_ = nil;
  [self sendLoginRequest];
  self.alertView = nil;
}


@end
