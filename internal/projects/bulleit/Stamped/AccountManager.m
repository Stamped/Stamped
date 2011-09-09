//
//  AccountManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "AccountManager.h"

#import <RestKit/CoreData/CoreData.h>

#import "StampedAppDelegate.h"
#import "FirstRunViewController.h"
#import "KeychainItemWrapper.h"
#import "OAuthToken.h"

NSString* const kCurrentUserHasUpdatedNotification = @"kCurrentUserHasUpdatedNotification";

static NSString* const kPasswordKeychainItemID = @"Password";
static NSString* const kAccessTokenKeychainItemID = @"AccessToken";
static NSString* const kRefreshTokenKeychainItemID = @"RefreshToken";
static NSString* const kClientID = @"stampedtest";
static NSString* const kClientSecret = @"august1ftw";
static NSString* const kLoginPath = @"/oauth2/login.json";
static NSString* const kRefreshPath = @"/oauth2/token.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";
static NSString* const kTokenExpirationUserDefaultsKey = @"TokenExpirationDate";
static AccountManager* sharedAccountManager_ = nil;

@interface AccountManager ()
- (void)sendLoginRequest;
- (void)sendTokenRefreshRequest;
- (void)sendUserInfoRequest;
- (void)showFirstRunViewController;
- (void)refreshTimerFired:(NSTimer*)theTimer;

@property (nonatomic, retain) FirstRunViewController* firstRunViewController;
@end

@implementation AccountManager

@synthesize authToken = authToken_;
@synthesize currentUser = currentUser_;
@synthesize delegate = delegate_;
@synthesize authenticated = authenticated_;
@synthesize firstRunViewController = firstRunViewController_;

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
    oAuthRequestQueue_ = [[RKRequestQueue alloc] init];
    oAuthRequestQueue_.delegate = self;
    oAuthRequestQueue_.concurrentRequestsLimit = 1;
    [oAuthRequestQueue_ start];
  }
  return self;
}

- (void)refreshToken {
  [RKClient sharedClient].requestQueue.suspended = YES;
  [self sendTokenRefreshRequest];
}

- (void)showFirstRunViewController {
  [oAuthRequestQueue_ cancelAllRequests];

  self.firstRunViewController = [[FirstRunViewController alloc] initWithNibName:@"FirstRunViewController" bundle:nil];
  firstRunViewController_.delegate = self;
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController presentModalViewController:firstRunViewController_ animated:YES];
  [self.firstRunViewController release];
}

- (void)authenticate {
  NSString* screenName = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  if (screenName.length > 0) {
    self.currentUser = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", screenName]];
  } else {
    [self showFirstRunViewController];
    return;
  }
  NSDate* tokenExpirationDate = [[NSUserDefaults standardUserDefaults] objectForKey:kTokenExpirationUserDefaultsKey];
  // Fresh install.
  if (!tokenExpirationDate) {
    [self showFirstRunViewController];
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
    [RKClient sharedClient].requestQueue.suspended = NO;
    [self sendUserInfoRequest];
    authenticated_ = YES;
    [self.delegate accountManagerDidAuthenticate];
    firstRun_ = NO;
  }
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.response isUnauthorized] &&
      [objectLoader.resourcePath rangeOfString:kUserLookupPath].location != NSNotFound) {
    [self refreshToken];
    return;
  }

  if ([objectLoader.resourcePath isEqualToString:kLoginPath]) {
    [self.firstRunViewController signInFailed:nil];
    return;
  } else if ([objectLoader.resourcePath isEqualToString:kRefreshPath]) {
    [self sendLoginRequest];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  if ([object isKindOfClass:[User class]]) {
    self.currentUser = (User*)object;
    [[NSNotificationCenter defaultCenter] postNotificationName:kCurrentUserHasUpdatedNotification
                                                        object:self];
    return;
  }
  
  OAuthToken* token = object;
  if ([objectLoader.resourcePath isEqualToString:kLoginPath]) {
    self.firstRunViewController.delegate = nil;
    [self.firstRunViewController.parentViewController dismissModalViewControllerAnimated:YES];
    self.firstRunViewController = nil;

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
    authenticated_ = YES;
    [self.delegate accountManagerDidAuthenticate];
    firstRun_ = NO;
  }
  [RKClient sharedClient].requestQueue.suspended = NO;
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
      username, @"login",
      password, @"password",
      kClientID, @"client_id",
      kClientSecret, @"client_secret", nil];
  [oAuthRequestQueue_ addRequest:objectLoader];
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
  [oAuthRequestQueue_ addRequest:objectLoader];
}

- (void)sendUserInfoRequest {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath delegate:self];
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithKeysAndObjects:@"screen_names", username, nil];
  [objectLoader send];
}

- (void)refreshTimerFired:(NSTimer*)theTimer {
  [self sendTokenRefreshRequest];
}

#pragma mark - FirstRunViewControllerDelegate methods.

- (void)viewController:(FirstRunViewController*)viewController 
    didReceiveUsername:(NSString*)username 
              password:(NSString*)password {
  if (username.length > 0 && password.length > 0) {
    [passwordKeychainItem_ setObject:username forKey:(id)kSecAttrAccount];
    [passwordKeychainItem_ setObject:password forKey:(id)kSecValueData];
    [self sendLoginRequest];
  } else {
    [viewController signInFailed:nil];
  }
}

#pragma mark - RKRequestQueueDelegate methods.

- (void)requestQueue:(RKRequestQueue*)queue willSendRequest:(RKRequest*)request {
  [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
  if (queue == oAuthRequestQueue_) {
    [RKClient sharedClient].requestQueue.suspended = YES;
  } else if (queue == [RKClient sharedClient].requestQueue) {
    if (!self.authToken.accessToken) {
      [self refreshToken];
      return;
    }

    if ([request.params isKindOfClass:[RKParams class]]) {
      [(RKParams*)request.params setValue:self.authToken.accessToken forParam:@"oauth_token"];
      return;
    }
    
    // Wrap shiz with the current oauth token.
    NSMutableDictionary* params =
        [NSMutableDictionary dictionaryWithDictionary:(NSDictionary*)request.params];

    [params setObject:self.authToken.accessToken forKey:@"oauth_token"];
    request.params = params;
    
    if (request.isGET) {
      request.resourcePath = [request.resourcePath appendQueryParams:params];
      request.params = nil;
    }
  }
  NSLog(@"Request: %@", request.resourcePath);
}

- (void)requestQueueDidFinishLoading:(RKRequestQueue*)queue {
  if (queue.count == 0)
    [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
}

@end
