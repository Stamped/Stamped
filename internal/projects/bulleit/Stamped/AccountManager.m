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
static const NSUInteger kMaxAuthRetries = 10;
static AccountManager* sharedAccountManager_ = nil;

@interface AccountManager ()
- (void)sendLoginRequest;
- (void)sendTokenRefreshRequest;
- (void)sendUserInfoRequest;
- (void)showAuthAlert;
- (void)refreshTimerFired:(NSTimer*)theTimer;
- (void)reachabilityDidChange:(NSNotification*)notification;
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

    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(reachabilityDidChange:)
                                                 name:RKReachabilityStateChangedNotification 
                                               object:nil];
  }
  return self;
}

- (void)reachabilityDidChange:(NSNotification*)notification {
  RKReachabilityObserver* observer = (RKReachabilityObserver*)[notification object];
  RKReachabilityNetworkStatus status = [observer networkStatus];
  if ((status == RKReachabilityReachableViaWiFi || status == RKReachabilityReachableViaWWAN) && firstRun_) {
    [self authenticate];
  }
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
    [self.delegate accountManagerDidAuthenticate];
    [self sendTokenRefreshRequest];
    firstRun_ = NO;
  }
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"Error: %@", error);
  if ([objectLoader.resourcePath isEqualToString:kLoginPath]) {
    NSLog(@"Login path failed.");
    if (numRetries_++ < kMaxAuthRetries) {
      [self performSelector:@selector(sendLoginRequest)
                 withObject:self
                 afterDelay:1.0];
      return;
    }
    [self showAuthAlert];
    return;
  } else if ([objectLoader.resourcePath isEqualToString:kRefreshPath]) {
    NSLog(@"refresh path failed.");
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
    NSLog(@"Got refresh token: %@", token.refreshToken);
    [refreshTokenKeychainItem_ setObject:@"RefreshToken" forKey:(id)kSecAttrAccount];
    [refreshTokenKeychainItem_ setObject:token.refreshToken forKey:(id)kSecValueData];
    self.authToken = token;
  }
  NSLog(@"got access token: %@", token.accessToken);
  [refreshTokenKeychainItem_ setObject:@"AccessToken" forKey:(id)kSecAttrAccount];
  [accessTokenKeychainItem_ setObject:token.accessToken forKey:(id)kSecValueData];
  self.authToken.accessToken = token.accessToken;

  oauthRefreshTimer_ = [NSTimer scheduledTimerWithTimeInterval:token.lifetimeSecs
                                                        target:self 
                                                      selector:@selector(refreshTimerFired:)
                                                      userInfo:nil 
                                                       repeats:NO];
  if (firstRun_) {
    [self.delegate accountManagerDidAuthenticate];
    firstRun_ = NO;
  }

  [self sendUserInfoRequest];
}

- (void)sendLoginRequest {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  NSLog(@"sending login request");
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* oauthMapping = [objectManager.mappingProvider mappingForKeyPath:@"OAuthToken"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kLoginPath
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = oauthMapping;
  NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  NSString* password = [passwordKeychainItem_ objectForKey:(id)kSecValueData];
  NSLog(@"Username: %@, password: %@", username, password);
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

  NSLog(@"sending token refresh request.");
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

  NSLog(@"sending user info request...");
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  NSString* resourcePath = [NSString stringWithFormat:@"/users/lookup.json?screen_names=%@&oauth_token=%@", username, self.authToken.accessToken];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:userMapping
                                  delegate:self];
}

- (void)refreshTimerFired:(NSTimer*)theTimer {
  NSLog(@"timer fired.");
  [self sendTokenRefreshRequest];
  oauthRefreshTimer_ = nil;
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
