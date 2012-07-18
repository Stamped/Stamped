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

//#if defined (DEV_BUILD)
static NSString* const _baseURL = @"https://api1.stamped.com/v1";
//#else
//static NSString* const _baseURL = @"https://api1.stamped.com/v1";
//#endif

static NSString* const _clientID = @"iphone8@2x";
static NSString* const _clientSecret = @"LnIFbmL0a75G8iQeHCV8VOT4fWFAWhzu";

static NSString* const _refreshPath = @"/oauth2/token.json";


NSString* const STRestKitLoaderErrorDomain = @"STRestKitLoaderErrorDomain";
NSString* const STRestKitErrorIDKey = @"STRestKitErrorIDKey";

@interface STRestKitLoaderHelper : NSObject <RKObjectLoaderDelegate, STCancellationDelegate>

- (id)initWithPath:(NSString*)path 
        authPolicy:(STRestKitAuthPolicy)policy
              post:(BOOL)post 
            params:(NSDictionary*)params 
           mapping:(RKObjectMapping*)mapping
          Callback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readonly, retain) STCancellation* cancellation;
@property (nonatomic, readonly, assign) STRestKitAuthPolicy policy;
@property (nonatomic, readonly, assign) BOOL post;
@property (nonatomic, readonly, assign) NSString* path;
@property (nonatomic, readonly, retain) NSDictionary* params;
@property (nonatomic, readonly, copy) void(^callback)(NSArray*,NSError*,STCancellation*);
@property (nonatomic, readonly, retain) NSTimer* timer;
@property (nonatomic, readonly, retain) RKObjectMapping* mapping;

@end

@interface STRestKitLoader() <RKRequestQueueDelegate>

+ (NSError*)errorWithCode:(STRestKitLoaderError)code andDescription:(NSString*)string;

- (void)helperDidCancel:(STRestKitLoaderHelper*)helper;

- (void)helperDidTimeout:(STRestKitLoaderHelper*)helper;

- (void)helper:(STRestKitLoaderHelper*)helper didFailWithObjectLoader:(RKObjectLoader*)objectLoader andError:(NSError*)error;

- (void)helper:(STRestKitLoaderHelper*)helper didLoadWithObjectLoader:(RKObjectLoader*)objectLoader andObjects:(NSArray*)objects;

@property (nonatomic, readwrite, retain) STSimpleOAuthToken* authToken;

@property (nonatomic, readwrite, retain) id<STUserDetail> currentUser;
@property (nonatomic, readonly, retain) RKObjectManager* objectManager;
@property (nonatomic, readonly, retain) NSMutableArray* pendingRequests;
@property (nonatomic, readonly, retain) NSMutableArray* waitingRequests;

@property (nonatomic, readonly, retain) RKRequestQueue* authRequestQueue;
@property (nonatomic, readonly, retain) KeychainItemWrapper* passwordKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* twitterUserTokenKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* twitterUserSecretKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* facebookUserTokenKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* accessTokenKeychainItem;
@property (nonatomic, readonly, retain) KeychainItemWrapper* refreshTokenKeychainItem;

@property (nonatomic, readwrite, retain) STCancellation* refreshTokenCancellation;
@property (nonatomic, readwrite, retain) STCancellation* loginCancellation;

@property (nonatomic, readwrite, retain) NSTimer* refreshTimer;

@end

@implementation STRestKitLoaderHelper

@synthesize callback = callback_;
@synthesize cancellation = cancellation_;
@synthesize params = params_;
@synthesize post = post_;
@synthesize policy = policy_;
@synthesize path = path_;
@synthesize timer = timer_;
@synthesize mapping = mapping_;

- (id)initWithPath:(NSString*)path 
        authPolicy:(STRestKitAuthPolicy)policy
              post:(BOOL)post 
            params:(NSDictionary*)params 
           mapping:(RKObjectMapping*)mapping
          Callback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block
{
    self = [super init];
    if (self) {
        path_ = [path retain];
        policy_ = policy;
        post_ = post;
        mapping_= [mapping retain];
        timer_ = [[NSTimer timerWithTimeInterval:30 target:self selector:@selector(timeout:) userInfo:nil repeats:NO] retain];
        params_ = [params retain];
        callback_ = [block copy];
        cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
    }
    return self;
}

- (void)dealloc {
    [callback_ release];
    cancellation_.delegate = nil;
    [cancellation_ release];
    [params_ release];
    [timer_ release];
    [path_ release];
    [mapping_ release];
    [super dealloc];
}

- (void)timeout:(NSTimer*)timer {
    [[STRestKitLoader sharedInstance] helperDidTimeout:[[self retain] autorelease]];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
    [[STRestKitLoader sharedInstance] helperDidCancel:[[self retain] autorelease]];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
    [[STRestKitLoader sharedInstance] helper:[[self retain] autorelease] didFailWithObjectLoader:objectLoader andError:error];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
    [[STRestKitLoader sharedInstance] helper:[[self retain] autorelease] didLoadWithObjectLoader:objectLoader andObjects:objects];
}

@end

@implementation STRestKitLoader

@synthesize currentUser = _currentUser;
@synthesize authToken = _authToken;

@synthesize objectManager = _objectManager;

@synthesize authRequestQueue = _authRequestQueue;
@synthesize passwordKeychainItem = _passwordKeychainItem;
@synthesize twitterUserTokenKeychainItem = _twitterUserTokenKeychainItem;
@synthesize twitterUserSecretKeychainItem = _twitterUserSecretKeychainItem;
@synthesize facebookUserTokenKeychainItem = _facebookUserTokenKeychainItem;
@synthesize accessTokenKeychainItem = _accessTokenKeychainItem;
@synthesize refreshTokenKeychainItem = _refreshTokenKeychainItem;

@synthesize refreshTokenCancellation = _refreshTokenCancellation;
@synthesize loginCancellation = _loginCancellation;

@synthesize refreshTimer = _refreshTimer;
@synthesize pendingRequests = _pendingRequests;
@synthesize waitingRequests = _waitingRequests;


static NSString* const _passwordKeychainItemID = @"Password";
static NSString* const _twitterUserTokenKeychainItemID = @"TwitterUserToken";
static NSString* const _twitterUserSecretKeychainItemID = @"TwitterUserSecret";
static NSString* const _facebookUserTokenKeychainItemID = @"FacebookUserToken";
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

+ (NSError*)errorWithCode:(STRestKitLoaderError)code andDescription:(NSString*)string {
    return [NSError errorWithDomain:STRestKitLoaderErrorDomain
                               code:code
                           userInfo:[NSDictionary dictionaryWithObject:string forKey:NSLocalizedDescriptionKey]];
}

- (id)init {
    self = [super init];
    if (self) {
        
        _pendingRequests = [[NSMutableArray alloc] init];
        _waitingRequests = [[NSMutableArray alloc] init];
        
        _authToken = [[STSimpleOAuthToken alloc] init];
        
        _objectManager = [[RKObjectManager objectManagerWithBaseURL:_baseURL] retain];
        
        _objectManager.requestQueue.delegate = self;
        _objectManager.requestQueue.concurrentRequestsLimit = 1;
        [_objectManager.requestQueue start];
        
        _authRequestQueue = [[RKRequestQueue alloc] init];
        _authRequestQueue.delegate = self;
        _authRequestQueue.concurrentRequestsLimit = 1;
        _authRequestQueue.requestTimeout = 35;
        [RKClient sharedClient].requestQueue.requestTimeout = 35;
        [_authRequestQueue start];
        
        NSAssert1(_authRequestQueue != _objectManager.requestQueue, @"Auth queue should not be equal to normal queue %@", _authRequestQueue);
        
        [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss.SSSSSS" inTimeZone:nil];
        [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss" inTimeZone:nil];
        
        _passwordKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_passwordKeychainItemID];
        _twitterUserTokenKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_twitterUserTokenKeychainItemID];
        _twitterUserSecretKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_twitterUserSecretKeychainItemID];
        _facebookUserTokenKeychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_facebookUserTokenKeychainItemID];
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
    //Not ever going to happen, singleton
    [_pendingRequests release];
    [_waitingRequests release];
    
    [_currentUser release];
    [_authToken release];
    
    [_objectManager release];
    
    [_authRequestQueue release];
    
    [_passwordKeychainItem release];
    [_twitterUserTokenKeychainItem release];
    [_twitterUserSecretKeychainItem release];
    [_facebookUserTokenKeychainItem release];
    [_accessTokenKeychainItem release];
    [_refreshTokenKeychainItem release];
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)helper:(STRestKitLoaderHelper*)helper finishWithObjects:(NSArray*)objects andError:(NSError*)error {
    helper.cancellation.delegate = nil;
    if (!helper.cancellation.cancelled && helper.callback) {
        helper.callback(objects, error, helper.cancellation);
    }
    [helper.cancellation cancel];
}

- (void)autoreleaseHelper:(STRestKitLoaderHelper*)helper {
    [[helper retain] autorelease];
    [self.pendingRequests removeObject:helper];
    [self.waitingRequests removeObject:helper];
}

- (void)processHelper:(STRestKitLoaderHelper*)helper {
    
    RKObjectManager* objectManager = [RKObjectManager sharedManager];
    RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:helper.path
                                                                      delegate:helper];
    if (helper.post) {
        objectLoader.method = RKRequestMethodPOST;
    }
    NSMutableDictionary* paramsCopy = [NSMutableDictionary dictionaryWithDictionary:helper.params];
    BOOL putOntoWaitQueue = NO;
    if (helper.policy != STRestKitAuthPolicyStampedAuth && helper.policy != STRestKitAuthPolicyNone) {
        NSString* accessToken = self.authToken.accessToken;
        if (accessToken) {
            [paramsCopy setObject:accessToken forKey:@"oauth_token"];
        }
        else {
            if (helper.policy == STRestKitAuthPolicyFail || helper.policy == STRestKitAuthPolicyWait) {
                if (helper.policy == STRestKitAuthPolicyFail || !self.loggedIn) {
                    NSError* error = nil;
                    if (helper.policy == STRestKitAuthPolicyFail) {
                        error = [STRestKitLoader errorWithCode:STRestKitLoaderErrorRefreshing
                                                andDescription:@"Token was refreshing"];
                    }
                    else {
                        error = [STRestKitLoader errorWithCode:STRestKitLoaderErrorLoggedOut
                                                andDescription:[NSString stringWithFormat:@"Must be logged in to complete this operation.%d,%d", self.loggedIn, helper.policy] ];
                    }
                    [Util executeOnMainThread:^{
                        [self helper:helper finishWithObjects:nil andError:error];
                    }];
                }
                else {
                    putOntoWaitQueue = YES;
                }
            }
        }
    }
    
    objectLoader.objectMapping = helper.mapping;
    
    STCancellation* can = [[helper.cancellation retain] autorelease];
    can.decoration = [NSString stringWithFormat:@"RestKit:%@ %@", objectLoader.resourcePath, objectLoader.params];
    
    // NSLog(@"RestKit:%@-%@",path, params);
    
    if (putOntoWaitQueue) {
        [self.waitingRequests addObject:helper];
    }
    else {
        objectLoader.params = paramsCopy;
        if (helper.policy != STRestKitAuthPolicyStampedAuth) {
            [objectManager.requestQueue addRequest:objectLoader];
        }
        else {
            [self.authRequestQueue addRequest:objectLoader];
        }
    }
}

- (void)helperDidTimeout:(STRestKitLoaderHelper *)helper {
    [helper.timer invalidate];
    [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:helper];
    [self helper:helper finishWithObjects:nil andError:[STRestKitLoader errorWithCode:STRestKitLoaderErrorTimeout andDescription:@"Server was not responding"]];
    [self autoreleaseHelper:helper];
}

- (void)helperDidCancel:(STRestKitLoaderHelper *)helper {
    [helper.timer invalidate];
    [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:helper];
    [self autoreleaseHelper:helper];
}

- (void)helper:(STRestKitLoaderHelper *)helper didFailWithObjectLoader:(RKObjectLoader *)objectLoader andError:(NSError *)error {
    id<RKParser> parser = [[RKParserRegistry sharedRegistry] parserForMIMEType:objectLoader.response.MIMEType];
    NSString* errorMessage = nil;
    NSString* errorID = nil;
    if (parser) {
        NSString* body = objectLoader.response.bodyAsString;
        if (body) {
            NSDictionary* errorDict = [parser objectFromString:objectLoader.response.bodyAsString error:nil];
            errorMessage = [errorDict objectForKey:@"message"];
            errorID = [errorDict objectForKey:@"error"];
        }
    }
    if (!errorMessage) {
        errorMessage = @"We're experiencing some difficulties. Please try again later.";
    }
    if (!errorID) {
        errorID = @"unknown";
    }
    NSInteger httpCode = objectLoader.response.statusCode;
    error = [NSError errorWithDomain:error.domain code:error.code userInfo:[NSDictionary dictionaryWithObjectsAndKeys:
                                                                            errorMessage, NSLocalizedDescriptionKey,
                                                                            errorID, STRestKitErrorIDKey,
                                                                            nil]];
    [STDebug log:[NSString stringWithFormat:
                  @"RestKit: Failed request with %d:\n%@\n%@\n%@",
                  httpCode,
                  objectLoader.resourcePath,
                  objectLoader.params,
                  error]];
    BOOL retry = NO;
    if (httpCode == 401 && [errorID isEqualToString:@"invalid_token"]) {
        if (objectLoader.queue == [STRestKitLoader sharedInstance].authRequestQueue) {
            NSAssert1(helper.policy == STRestKitAuthPolicyStampedAuth, @"bad policy, should be Auth was %2", helper.policy);
            if ([helper.path isEqualToString:_refreshPath]) {
                //fail so login can be handled
            }
            else {
                [STStampedAPI logError:[NSString stringWithFormat:@"Unknown auth op\npath=%@\nparams=%@", helper.path, helper.params]];
            }
        }
        else {
            [[STRestKitLoader sharedInstance] refreshToken];
            if (helper.policy == STRestKitAuthPolicyWait) {
                retry = YES;
            }
        }
    }
    else if (httpCode == 401 && [errorID isEqualToString:@"facebook_auth"]) {
        
    }
    if (retry) {
        [self autoreleaseHelper:helper];
        [self processHelper:helper];
    }
    else {
        [helper.timer invalidate];
        [self helper:helper finishWithObjects:nil andError:error];
        [self autoreleaseHelper:helper];
    }
}

- (void)helper:(STRestKitLoaderHelper *)helper didLoadWithObjectLoader:(RKObjectLoader *)objectLoader andObjects:(NSArray *)objects {
    [helper.timer invalidate];
    [self helper:helper finishWithObjects:objects andError:nil];
    [self autoreleaseHelper:helper];
}

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                     authPolicy:(STRestKitAuthPolicy)policy
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
    NSAssert1(path, @"Path must not be nil %@", params);
    NSAssert1(params, @"Params must not be nil %@", path);
    NSAssert1(mapping, @"Mapping must not be nil %@", mapping);
    RKClient* client = [RKClient sharedClient];
    if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
        //NSLog(@"Offline");
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(nil, [NSError errorWithDomain:STRestKitLoaderErrorDomain 
                                               code:STRestKitLoaderErrorNotConnected
                                           userInfo:[NSDictionary dictionaryWithObject:@"You are not connected to the internet." forKey:NSLocalizedDescriptionKey]
                            ], cancellation);
                cancellation.delegate = nil;
            }
        }];
        return cancellation;
    }
    else {
        STRestKitLoaderHelper* helper = [[[STRestKitLoaderHelper alloc] initWithPath:path
                                                                          authPolicy:policy
                                                                                post:post
                                                                              params:params 
                                                                             mapping:mapping
                                                                            Callback:block] autorelease];
        [self processHelper:helper];
        return helper.cancellation;
    }
}

- (void)cancelHelper:(STRestKitLoaderHelper*)helper {
    [helper.cancellation cancel];
}

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                        authPolicy:(STRestKitAuthPolicy)policy
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block {
    return [self loadWithPath:path 
                         post:post 
                   authPolicy:policy
                       params:params 
                      mapping:mapping 
                  andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                      id result = nil;
                      if (array) {
                          if (array.count > 0) {
                              result = [array objectAtIndex:0];
                          }
                          else {
                              result = [[[[mapping objectClass] alloc] init] autorelease];
                          }
                      }
                      block(result, error, cancellation);
                  }];
}

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                  authenticated:(BOOL)authenticated
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
    return [self loadWithPath:path
                         post:post
                   authPolicy:authenticated ? STRestKitAuthPolicyOptional : STRestKitAuthPolicyStampedAuth
                       params:params
                      mapping:mapping
                  andCallback:block];
}

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                     authenticated:(BOOL)authenticated
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block {
    return [self loadOneWithPath:path
                            post:post
                      authPolicy:authenticated ? STRestKitAuthPolicyOptional : STRestKitAuthPolicyStampedAuth
                          params:params
                         mapping:mapping
                     andCallback:block];;
}

#pragma mark - Auth

- (void)cancelAllWaitingRequests {
    NSArray* copy = [NSArray arrayWithArray:self.waitingRequests];
    [self.waitingRequests removeAllObjects];
    for (STRestKitLoaderHelper* helper in copy) {
        [helper.timer invalidate];
        [self helper:helper finishWithObjects:nil andError:[STRestKitLoader errorWithCode:STRestKitLoaderErrorLoggedOut andDescription:@"Task interrupted by logout"]];
        [self autoreleaseHelper:helper];
    }
}

- (void)performWaitingRequests {
    NSArray* copy = [NSArray arrayWithArray:self.waitingRequests];
    [self.waitingRequests removeAllObjects];
    for (STRestKitLoaderHelper* helper in copy) {
        [self processHelper:helper];
    }
}

- (void)handleAllWaitingRequests {
    if (self.authToken.accessToken) {
        [self performWaitingRequests];
    }
    else {
        if (!self.loggedIn) {
            [self cancelAllWaitingRequests];
        }
        else {
            //Keep waiting
        }
    }
}

- (void)storeOAuthToken:(id<STOAuthToken>)token {
    self.authToken.accessToken = nil;
    if (token.refreshToken) {
        [_refreshTokenKeychainItem setObject:_refreshTokenKeychainItemID forKey:(id)kSecAttrAccount];
        [_refreshTokenKeychainItem setObject:token.refreshToken forKey:(id)kSecValueData];
        self.authToken.refreshToken = token.refreshToken;
    }
    if (token.accessToken) {
        [_accessTokenKeychainItem setObject:_accessTokenKeychainItemID forKey:(id)kSecAttrAccount];
        [_accessTokenKeychainItem setObject:token.accessToken forKey:(id)kSecValueData];
        self.authToken.accessToken = token.accessToken;
        [Util executeOnMainThread:^{
            [self handleAllWaitingRequests]; 
        }];
    }
    if (token.lifespanInSeconds) {
        [[NSUserDefaults standardUserDefaults] setObject:[NSDate dateWithTimeIntervalSinceNow:token.lifespanInSeconds.floatValue] forKey:_tokenExpirationUserDefaultsKey];
    }
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

- (void)setCurrentUser:(id<STUserDetail>)userDetail {
    [_currentUser autorelease];
    _currentUser = [userDetail retain];
    if (userDetail) {
        NSData* data = [NSKeyedArchiver archivedDataWithRootObject:userDetail];
        [[NSUserDefaults standardUserDefaults] setObject:data forKey:_userDataUserDefaultsKey];
    }
    else {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:_userDataUserDefaultsKey];
    }
    [[NSUserDefaults standardUserDefaults] synchronize];
}

- (void)clearAuthState {
    [_passwordKeychainItem resetKeychainItem];
    [_twitterUserTokenKeychainItem resetKeychainItem];
    [_twitterUserSecretKeychainItem resetKeychainItem];
    [_facebookUserTokenKeychainItem resetKeychainItem];
    [_accessTokenKeychainItem resetKeychainItem];
    [_refreshTokenKeychainItem resetKeychainItem];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:_tokenExpirationUserDefaultsKey];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:_loginTypeUserDefaultsKey];
    self.currentUser = nil;
    self.authToken.refreshToken = nil;
    self.authToken.accessToken = nil;
    [[NSUserDefaults standardUserDefaults] synchronize];
    [self cancelAllWaitingRequests];
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
            if (username.length && password.length) {
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
            NSString* path = @"/oauth2/login/facebook.json";
            NSString* userToken = [_facebookUserTokenKeychainItem objectForKey:(id)kSecValueData];
            if (userToken.length) {
                [params setObject:userToken forKey:@"user_token"];
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
        else {
            NSAssert1([loginType isEqualToString:_loginTypeTwitter], @"Unrecognized login type %@", loginType);
            NSString* path = @"/oauth2/login/twitter.json";
            NSString* userToken = [_twitterUserTokenKeychainItem objectForKey:(id)kSecValueData];
            NSString* userSecret = [_twitterUserSecretKeychainItem objectForKey:(id)kSecValueData];
            if (userToken.length && userSecret.length) {
                [params setObject:userToken forKey:@"user_token"];
                [params setObject:userSecret forKey:@"user_secret"];
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
    }
}

- (STCancellation*)sendTokenRefreshRequestWithCallback:(void (^)(id<STOAuthToken> token, NSError* error, STCancellation* cancellation))block {
    NSString* refreshToken = [_refreshTokenKeychainItem objectForKey:(id)kSecValueData];
    if (refreshToken.length) {
        NSString* path = _refreshPath;
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

- (void)storeStampedScreenName:(NSString*)screenName andPassword:(NSString*)password {
    [_passwordKeychainItem setObject:screenName forKey:kSecAttrAccount];
    [_passwordKeychainItem setObject:password forKey:kSecValueData];
    [[NSUserDefaults standardUserDefaults] setObject:_loginTypeStamped forKey:_loginTypeUserDefaultsKey];
}

- (void)storeFacebookUserToken:(NSString*)userToken {
    [_facebookUserTokenKeychainItem setObject:_facebookUserTokenKeychainItemID forKey:kSecAttrAccount];
    [_facebookUserTokenKeychainItem setObject:userToken forKey:kSecValueData];
    [[NSUserDefaults standardUserDefaults] setObject:_loginTypeFacebook forKey:_loginTypeUserDefaultsKey];
}

- (void)storeTwitterUserToken:(NSString*)userToken andUserSecret:(NSString*)userSecret {
    [_twitterUserTokenKeychainItem setObject:_twitterUserTokenKeychainItemID forKey:kSecAttrAccount];
    [_twitterUserTokenKeychainItem setObject:userToken forKey:kSecValueData];
    [_twitterUserSecretKeychainItem setObject:_twitterUserSecretKeychainItemID forKey:kSecAttrAccount];
    [_twitterUserSecretKeychainItem setObject:userSecret forKey:kSecValueData];
    [[NSUserDefaults standardUserDefaults] setObject:_loginTypeTwitter forKey:_loginTypeUserDefaultsKey];
}

- (NSMutableDictionary*)_clientParams {
    return [NSMutableDictionary dictionaryWithObjectsAndKeys:
            _clientID, @"client_id",
            _clientSecret, @"client_secret",
            nil];
}

- (STCancellation*)_loginWithPath:(NSString*)path 
                           params:(NSDictionary*)params
                 storeCredentials:(void (^)(id<STLoginResponse> response))store 
                      andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* paramCopy = [NSMutableDictionary dictionaryWithDictionary:params];
    [paramCopy setObject:_clientID forKey:@"client_id"];
    [paramCopy setObject:_clientSecret forKey:@"client_secret"];
    return [self loadOneWithPath:path
                            post:YES
                   authenticated:NO
                          params:paramCopy
                         mapping:[STSimpleLoginResponse mapping]
                     andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                         id<STLoginResponse> response = result;
                         if (response) {
                             store(response);
                             [self storeOAuthToken:response.token];
                             self.currentUser = response.user;
                         }
                         block(result, error, cancellation);
                         if (response) {
                             store(response);
                             [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPILoginNotification object:nil];
                             [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPIUserUpdatedNotification object:nil];
                         }
                     }];
}

- (STCancellation*)loginWithScreenName:(NSString*)screenName 
                              password:(NSString*)password 
                           andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/oauth2/login.json";
    return [self _loginWithPath:path
                         params:[NSDictionary dictionaryWithObjectsAndKeys:
                                 screenName, @"login",
                                 password, @"password",
                                 nil]
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeStampedScreenName:screenName andPassword:password];
               } andCallback:block];
}

- (STCancellation*)loginWithFacebookUserToken:(NSString*)userToken
                                  andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/oauth2/login/facebook.json";
    return [self _loginWithPath:path
                         params:[NSDictionary dictionaryWithObject:userToken forKey:@"user_token"]
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeFacebookUserToken:userToken];
               } andCallback:block];
}

- (STCancellation*)loginWithTwitterUserToken:(NSString*)userToken 
                                  userSecret:(NSString*)userSecret
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSString* path = @"/oauth2/login/twitter.json";
    return [self _loginWithPath:path
                         params:[NSDictionary dictionaryWithObjectsAndKeys:
                                 userToken, @"user_token",
                                 userSecret, @"user_secret",
                                 nil]
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeTwitterUserToken:userToken andUserSecret:userSecret];
               } andCallback:block];
    
}

- (STCancellation*)createAccountWithPassword:(NSString*)password
                           accountParameters:(STAccountParameters*)accountParameters
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* params = [accountParameters asDictionaryParams];
    [params setObject:password forKey:@"password"];
    return [self _loginWithPath:@"/account/create.json"
                         params:params
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeStampedScreenName:accountParameters.screenName andPassword:password];
               } andCallback:block];
}

- (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
                                    accountParameters:(STAccountParameters*)accountParameters
                                          andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* params = [accountParameters asDictionaryParams];
    [params setObject:userToken forKey:@"user_token"];
    return [self _loginWithPath:@"/account/create/facebook.json"
                         params:params
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeFacebookUserToken:userToken];
               } andCallback:block];
}

- (STCancellation*)createAccountWithTwitterUserToken:(NSString*)userToken 
                                          userSecret:(NSString*)userSecret
                                   accountParameters:(STAccountParameters*)accountParameters
                                         andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block {
    NSMutableDictionary* params = [accountParameters asDictionaryParams];
    [params setObject:userToken forKey:@"user_token"];
    [params setObject:userSecret forKey:@"user_secret"];
    return [self _loginWithPath:@"/account/create/twitter.json"
                         params:params
               storeCredentials:^(id<STLoginResponse> response) {
                   [self storeTwitterUserToken:userToken andUserSecret:userSecret];
               } andCallback:block];
}

- (void)authenticate {
    NSDate* tokenExpirationDate = [[NSUserDefaults standardUserDefaults] objectForKey:_tokenExpirationUserDefaultsKey];
    // Fresh install.
    if (!tokenExpirationDate) {
        //NSLog(@"tokenExpirationDate not found");
        [[UIApplication sharedApplication] unregisterForRemoteNotifications];
        [self clearAuthState];
        [Util launchFirstRun];
    }
    else {
        //NSLog(@"tokenExpirationDate found");
        NSData* userData = [[NSUserDefaults standardUserDefaults] objectForKey:_userDataUserDefaultsKey];
        NSString* refreshToken = [_refreshTokenKeychainItem objectForKey:(id)kSecValueData];
        if (userData && refreshToken.length) {
            //NSLog(@"user and refresh token found");
            self.authToken.refreshToken = refreshToken;
            self.currentUser = [NSKeyedUnarchiver unarchiveObjectWithData:userData];
            NSTimeInterval timeUntilTokenRefresh = [tokenExpirationDate timeIntervalSinceNow];
            NSString* accessToken = [_accessTokenKeychainItem objectForKey:(id)kSecValueData];
            if (accessToken.length && timeUntilTokenRefresh > 0) {
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
            //NSLog(@"user and refresh token not found: %@, %@", userData, refreshToken);
            [self clearAuthState];
            [Util launchFirstRun];
        }
    }
}

- (BOOL)loggedIn {
    return self.authToken.refreshToken != nil;
}

- (void)refreshToken {
    if (!self.refreshTokenCancellation && self.authToken.refreshToken) {
        STCancellation* cancellation = [self sendTokenRefreshRequestWithCallback:^(id<STOAuthToken> token, NSError *error, STCancellation *cancellation) {
            self.refreshTokenCancellation = nil;
            if (token) {
                self.authToken.accessToken = token.accessToken;
                [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPIRefreshedTokenNotification object:nil];
            }
            else {
                [self clearAuthState];
            }
        }];
        if (cancellation) {
            self.refreshTokenCancellation = cancellation;
        }
        else {
            [self clearAuthState];
            [STDebug log:@"REPORT THIS: Refresh Token failed!"];
            [Util launchFirstRun];
        }
    }
}

- (void)logout {
    [self clearAuthState];
    [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPILogoutNotification object:nil];
    [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPIUserUpdatedNotification object:nil];
}

#pragma mark - RKRequestQueueDelegate methods.

- (void)requestQueue:(RKRequestQueue*)queue willSendRequest:(RKRequest*)request {
    [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
    if (queue == _authRequestQueue) {
        //NSLog(@"releasing auth lock");
        [RKClient sharedClient].requestQueue.suspended = YES;
    } 
    else if (queue == [RKClient sharedClient].requestQueue) {
        if (!self.authToken.accessToken) {
            [self refreshToken];
        }
        if ([request.params isKindOfClass:[RKParams class]]) {
            return;
        }
        NSMutableDictionary* params = [NSMutableDictionary dictionaryWithDictionary:(NSDictionary*)request.params];
        if (request.isGET /*&& [request.URL isKindOfClass:[RKURL class]]*/) {
            request.resourcePath = [request.resourcePath appendQueryParams:params];
            request.params = nil;
        }
        
        if (request.isPOST && request.params) {
            //NSLog(@"NOT GOOD, %@ %@", request.URL, request.params);
            request.params = [RKParams paramsWithDictionary:(id)request.params];
        }
    }
    else {
        NSAssert1(NO, @"Unknown queue %@", queue);
    }
}

- (void)requestQueueDidFinishLoading:(RKRequestQueue*)queue {
    if ([RKClient sharedClient].requestQueue.count == 0 && _authRequestQueue.count == 0) {
        [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    }
    if (queue == _authRequestQueue && queue.count == 0) {
        //NSLog(@"releasing auth lock");
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didLoadResponse:(RKResponse*)response {
    if (queue == _authRequestQueue) {
        //NSLog(@"releasing auth lock");
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didCancelRequest:(RKRequest*)request {
    if (queue == _authRequestQueue) {
        //NSLog(@"releasing auth lock");
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didFailRequest:(RKRequest*)request withError:(NSError*)error {
    if (queue == _authRequestQueue) {
        //NSLog(@"releasing auth lock");
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

#pragma mark - NSNotifications

- (void)appDidBecomeActive:(NSNotification*)notification {
    if (_authRequestQueue.count == 0)
        [RKClient sharedClient].requestQueue.suspended = NO;
}

- (void)updateCurrentUser:(id<STUserDetail>)currentUser {
    self.currentUser = currentUser;
    [[NSNotificationCenter defaultCenter] postNotificationName:STStampedAPIUserUpdatedNotification object:currentUser];
}


@end

