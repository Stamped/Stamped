//
//  STRestKitLoader.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRestKitLoader.h"
#import "Util.h"
#import "STDebug.h"
#import "STOAuthToken.h"
#import "KeyChainItemWrapper.h"
#import "STSimpleLoginResponse.h"
#import "STSimpleOAuthToken.h"

#if defined (DEV_BUILD)
static NSString* const _baseURL = @"https://dev.stamped.com/v0";
#else
static NSString* const _baseURL = @"https://api.stamped.com/v0";
#endif

static NSString* const _clientID = @"iphone8@2x";
static NSString* const _clientSecret = @"LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu";

@interface STRestKitLoaderHelper : NSObject <RKObjectLoaderDelegate, STCancellationDelegate>

- (id)initWithCallback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readonly, copy) void(^callback)(NSArray*,NSError*,STCancellation*);
@property (nonatomic, readonly, retain) STCancellation* cancellation;

@end

@implementation STRestKitLoaderHelper

@synthesize callback = callback_;
@synthesize cancellation = cancellation_;

- (id)initWithCallback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block
{
    self = [super init];
    if (self) {
        [self retain];
        callback_ = [block copy];
        cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
    }
    return self;
}

- (void)dealloc {
    [callback_ release];
    [cancellation_ release];
    [super dealloc];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
    //NSLog(@"Cancelled operation");
    [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
    [self autorelease];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
    [STDebug log:[NSString stringWithFormat:@"RestKit: Failed request with %d:\n%@\n%@ ", objectLoader.response.statusCode, objectLoader.URL, objectLoader.params]];
    if ([self.cancellation finish]) {
        [Util executeOnMainThread:^{
            self.callback(nil, error, self.cancellation);
            [self autorelease];
        }];
    }
    if ([objectLoader.response isUnauthorized]) {
        [[STRestKitLoader sharedInstance] refreshToken];
    }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
    //NSLog(@"RestKit Loaded %d objects for %@",objects.count, objectLoader.URL);
    if ([self.cancellation finish]) {
        [Util executeOnMainThread:^{
            self.callback(objects, nil, self.cancellation);
            [self autorelease];
        }];
    }
}

@end

@interface STRestKitLoader() <RKRequestQueueDelegate>

@property (nonatomic, readwrite, retain) id<STUserDetail> currentUser;
@property (nonatomic, readwrite, retain) STSimpleOAuthToken* authToken;

@property (nonatomic, readonly, retain) RKObjectManager* objectManager;

@property (nonatomic, readonly, retain) RKRequestQueue* authRequestQueue;
@property (nonatomic, readonly, retain) KeychainItemWrapper* passwordKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* accessTokenKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* refreshTokenKeychainItem;

@property (nonatomic, readwrite, retain) STCancellation* refreshTokenCancellation;
@property (nonatomic, readwrite, retain) STCancellation* loginCancellation;

@property (nonatomic, readwrite, retain) NSTimer* refreshTimer;

@end

@implementation STRestKitLoader

@synthesize currentUser = _currentUser;
@synthesize authToken = _authToken;

@synthesize objectManager = _objectManager;

@synthesize authRequestQueue = _authRequestQueue;
@synthesize passwordKeychainItem = _passwordKeychainItem;
@synthesize accessTokenKeychainItem = _accessTokenKeychainItem;
@synthesize refreshTokenKeychainItem = _refreshTokenKeychainItem;

@synthesize refreshTokenCancellation = _refreshTokenCancellation;
@synthesize loginCancellation = _loginCancellation;

@synthesize refreshTimer = _refreshTimer;


static NSString* const _passwordKeychainItemID = @"Password";
static NSString* const _accessTokenKeychainItemID = @"AccessToken";
static NSString* const _refreshTokenKeychainItemID = @"RefreshToken";
static NSString* const _loginTypeUserDefaultsKey = @"LoginType";
static NSString* const _tokenExpirationUserDefaultsKey = @"TokenExpirationDate";
static NSString* const _userDataUserDefaultsKey = @"UserData";

static NSString* const _loginTypeStamped = @"Stamped";
static NSString* const _loginTypeFacebook = @"Facebook";
static NSString* const _loginTypeTwitter = @"Twitter";


static STRestKitLoader* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STRestKitLoader alloc] init];
}

+ (STRestKitLoader*)sharedInstance {
    return _sharedInstance;
}

- (id)init {
    self = [super init];
    if (self) {
        
        _authToken = [[STSimpleOAuthToken alloc] init];
        
        _objectManager = [[RKObjectManager objectManagerWithBaseURL:_baseURL] retain];
        
        _objectManager.requestQueue.delegate = self;
        _objectManager.requestQueue.requestTimeout = 30;
        _objectManager.requestQueue.concurrentRequestsLimit = 1;
        
        _authRequestQueue = [[RKRequestQueue alloc] init];
        _authRequestQueue.requestTimeout = 30;
        _authRequestQueue.delegate = self;
        _authRequestQueue.concurrentRequestsLimit = 1;
        [_authRequestQueue start];
        
        _passwordKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_passwordKeychainItemID];
        _accessTokenKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_accessTokenKeychainItemID];
        _refreshTokenKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_refreshTokenKeychainItemID];
        
        [[NSNotificationCenter defaultCenter] addObserver:self
                                                 selector:@selector(appDidBecomeActive:)
                                                     name:UIApplicationDidBecomeActiveNotification
                                                   object:nil];
    }
    return self;
}

-(void)dealloc {
    [_currentUser release];
    [_authToken release];
    
    [_objectManager release];
    
    [_authRequestQueue release];
    
    [_passwordKeychainItem release];
    [_accessTokenKeychainItem release];
    [_refreshTokenKeychainItem release];
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                  authenticated:(BOOL)authenticated
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
    NSAssert1(path, @"Path must not be nil %@", params);
    NSAssert1(params, @"Params must not be nil %@", path);
    NSAssert1(mapping, @"Mapping must not be nil %@", mapping);
    if (self.objectManager.isOnline) {
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(nil, [NSError errorWithDomain:@"RestKit" 
                                               code:0 
                                           userInfo:[NSDictionary dictionaryWithObject:@"Not Online" forKey:@"Reason"]
                            ], cancellation);
                cancellation.delegate = nil;
            }
        }];
        return cancellation;
    }
    else {
        STRestKitLoaderHelper* helper = [[[STRestKitLoaderHelper alloc] initWithCallback:block] autorelease];    
        RKObjectManager* objectManager = [RKObjectManager sharedManager];
        RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path
                                                                          delegate:helper];
        if (post) {
            objectLoader.method = RKRequestMethodPOST;
        }
        
        NSMutableDictionary* paramsCopy = [NSMutableDictionary dictionaryWithDictionary:params];
        if (authenticated) {
            NSString* accessToken = self.authToken.accessToken;
            if (accessToken) {
                [paramsCopy setObject:self.authToken.accessToken forKey:@"oauth_token"];
            }
        }
        
        objectLoader.objectMapping = mapping;
        
        objectLoader.params = [[params copy] autorelease];
        
        // NSLog(@"RestKit:%@-%@",path, params);
        
        if (authenticated) {
            [objectManager.requestQueue addRequest:objectLoader];
        }
        else {
            [self.authRequestQueue addRequest:objectLoader];
        }
        STCancellation* can = [[helper.cancellation retain] autorelease];
        can.decoration = [NSString stringWithFormat:@"RestKit:%@ %@", objectLoader.resourcePath, objectLoader.params];
        return can;
    }
}

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                     authenticated:(BOOL)authenticated
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block {
    return [self loadWithPath:path 
                         post:post 
                authenticated:authenticated
                       params:params 
                      mapping:mapping 
                  andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                      id result = nil;
                      if (array && [array count] > 0) {
                          result = [array objectAtIndex:0];
                      }
                      block(result, error, cancellation);
                  }];
}

#pragma mark - Auth

- (void)storeOAuthToken:(id<STOAuthToken>)token {
    if (token.refreshToken) {
        [_refreshTokenKeychainItem setObject:_refreshTokenKeychainItemID forKey:(id)kSecAttrAccount];
        [_refreshTokenKeychainItem setObject:token.refreshToken forKey:(id)kSecValueData];
        self.authToken.refreshToken = token.refreshToken;
    }
    
    [_refreshTokenKeychainItem setObject:_accessTokenKeychainItemID forKey:(id)kSecAttrAccount];
    [_accessTokenKeychainItem setObject:token.accessToken forKey:(id)kSecValueData];
    
    [[NSUserDefaults standardUserDefaults] setObject:[NSDate dateWithTimeIntervalSinceNow:token.lifespanInSeconds.floatValue] forKey:_tokenExpirationUserDefaultsKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
    if (self.refreshTimer) {
        [self.refreshTimer invalidate];
    }
    self.refreshTimer = [NSTimer scheduledTimerWithTimeInterval:token.lifespanInSeconds.floatValue
                                                         target:self
                                                       selector:@selector(refreshTimerFired:)
                                                       userInfo:nil
                                                        repeats:YES];
}

- (void)updateUser:(id<STUserDetail>)userDetail {
    self.currentUser = userDetail;
}

- (void)clearAuthState {
    [_accessTokenKeychainItem resetKeychainItem];
    [_passwordKeychainItem resetKeychainItem];
    [_refreshTokenKeychainItem resetKeychainItem];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:_tokenExpirationUserDefaultsKey];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:_loginTypeUserDefaultsKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

- (void)refreshTimerFired:(NSTimer*)theTimer {
    [self refreshToken];
}

- (STCancellation*)sendLoginRequest:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSString* loginType = [[NSUserDefaults standardUserDefaults] objectForKey:_loginTypeUserDefaultsKey];
    if (!loginType) {
        return nil;
    }
    else { 
        NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                       _clientID, @"client_id",
                                       _clientSecret, @"client_secret",
                                       nil];
        if ([loginType isEqualToString:_loginTypeStamped]) {
            NSString* path = @"/oauth2/login.json";
            NSString* username = [_passwordKeychainItem objectForKey:(id)kSecAttrAccount];
            NSString* password = [_passwordKeychainItem objectForKey:(id)kSecValueData];
            if (username && password) {
                [params setObject:username forKey:@"login"];
                [params setObject:password forKey:@"password"];
                return [self loadOneWithPath:path
                                        post:YES
                               authenticated:NO
                                      params:params
                                     mapping:[STSimpleLoginResponse mapping]
                                 andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                     block(result, error, cancellation);
                                 }];
            }
            else {
                return nil;
            }
        }
        else if ([loginType isEqualToString:_loginTypeFacebook]) {
            return nil;
        }
        else {
            NSAssert1([loginType isEqualToString:_loginTypeTwitter], @"Unrecognized login type %@", loginType);
            return nil;
        }
    }
}

- (STCancellation*)sendTokenRefreshRequestWithCallback:(void (^)(id<STOAuthToken> token, NSError* error, STCancellation* cancellation))block {
    NSString* refreshToken = [_refreshTokenKeychainItem objectForKey:(id)kSecValueData];
    if (refreshToken) {
        NSString* path = @"/oauth2/token.json";
        NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:
                                refreshToken, @"refresh_token",
                                @"refresh_token", @"grant_type",
                                _clientID, @"client_id",
                                _clientSecret, @"client_secret",
                                nil];
        return [self loadOneWithPath:path
                                post:YES
                       authenticated:NO
                              params:params
                             mapping:[STSimpleOAuthToken mapping]
                         andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                             block(result, error, cancellation);
                         }];
    }
    else {
        return nil;
    }
}

- (void)loginWithStoredCredentials {
    
}

- (void)authenticate {
    
    NSDate* tokenExpirationDate = [[NSUserDefaults standardUserDefaults] objectForKey:_tokenExpirationUserDefaultsKey];
    // Fresh install.
    if (!tokenExpirationDate) {
        NSLog(@"tokenExpirationDate not found");
        [[UIApplication sharedApplication] unregisterForRemoteNotifications];
        [self clearAuthState];
        [Util launchFirstRun];
    }
    else {
        NSLog(@"tokenExpirationDate found");
        NSData* userData = [[NSUserDefaults standardUserDefaults] objectForKey:_userDataUserDefaultsKey];
        NSString* refreshToken = [_refreshTokenKeychainItem objectForKey:(id)kSecValueData];
        if (userData && refreshToken) {
            NSLog(@"user and refresh token found");
            self.authToken.refreshToken = refreshToken;
            self.currentUser = [NSKeyedUnarchiver unarchiveObjectWithData:userData];
            NSTimeInterval timeUntilTokenRefresh = [tokenExpirationDate timeIntervalSinceNow];
            NSString* accessToken = [_accessTokenKeychainItem objectForKey:(id)kSecValueData];
            if (accessToken && timeUntilTokenRefresh > 0) {
                self.authToken.accessToken = accessToken;
                self.refreshTimer = [NSTimer scheduledTimerWithTimeInterval:timeUntilTokenRefresh
                                                                     target:self
                                                                   selector:@selector(refreshTimerFired:)
                                                                   userInfo:nil
                                                                    repeats:YES];
            }
            else {
                [self refreshToken];
            }
        } else {
            NSLog(@"user and refresh token not found");
            [self clearAuthState];
            [Util launchFirstRun];
        }
    }
}

- (void)refreshToken {
    if (!self.refreshTokenCancellation) {
        STCancellation* cancellation = [self sendTokenRefreshRequestWithCallback:^(id<STOAuthToken> token, NSError *error, STCancellation *cancellation) {
            if (token) {
                self.authToken.accessToken = token.accessToken;
                
            }
        }];
        if (cancellation) {
            self.refreshTokenCancellation = cancellation;
        }
    }
}

#pragma mark - RKRequestQueueDelegate methods.

- (void)requestQueue:(RKRequestQueue*)queue willSendRequest:(RKRequest*)request {
    [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
    if (queue == _authRequestQueue) {
        [RKClient sharedClient].requestQueue.suspended = YES;
    } else if (queue == [RKClient sharedClient].requestQueue) {
        if (!self.authToken.accessToken) {
            [self refreshToken];
            return;
        }
        
        if ([request.params isKindOfClass:[RKParams class]]) {
            return;
        }
        
        NSMutableDictionary* params = [NSMutableDictionary dictionaryWithDictionary:(NSDictionary*)request.params];
        if (request.isGET && [request.URL isKindOfClass:[RKURL class]]) {
            request.resourcePath = [request.resourcePath appendQueryParams:params];
            request.params = nil;
        }
    }
}

- (void)requestQueueDidFinishLoading:(RKRequestQueue*)queue {
    if ([RKClient sharedClient].requestQueue.count == 0 && _authRequestQueue.count == 0) {
        [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    }
    if (queue == _authRequestQueue && queue.count == 0) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didLoadResponse:(RKResponse*)response {
    if (queue == _authRequestQueue) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didCancelRequest:(RKRequest*)request {
    if (queue == _authRequestQueue)
        [RKClient sharedClient].requestQueue.suspended = NO;
}

- (void)requestQueue:(RKRequestQueue*)queue didFailRequest:(RKRequest*)request withError:(NSError*)error {
    if (queue == _authRequestQueue) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

#pragma mark - NSNotifications

- (void)appDidBecomeActive:(NSNotification*)notification {
    if (_authRequestQueue.count == 0)
        [RKClient sharedClient].requestQueue.suspended = NO;
}


@end

