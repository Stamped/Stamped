//
//  AccountManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "AccountManager.h"

#import "STAppDelegate.h"
#import "FirstRunViewController.h"
#import "KeychainItemWrapper.h"
#import "OAuthToken.h"
#import "Util.h"
#import "SocialManager.h"
#import "GTMOAuthViewControllerTouch.h"

NSString* const kCurrentUserHasUpdatedNotification = @"kCurrentUserHasUpdatedNotification";
NSString* const kUserHasLoggedOutNotification = @"KUserHasLoggedOutNotification";

static NSString* const kPasswordKeychainItemID = @"Password";
static NSString* const kAccessTokenKeychainItemID = @"AccessToken";
static NSString* const kRefreshTokenKeychainItemID = @"RefreshToken";
static NSString* const kLoginPath = @"/oauth2/login.json";
static NSString* const kRefreshPath = @"/oauth2/token.json";
static NSString* const kRegisterPath = @"/account/create.json";
static NSString* const kUserLookupPath = @"/users/show.json";
static NSString* const kTokenExpirationUserDefaultsKey = @"TokenExpirationDate";
static AccountManager* sharedAccountManager_ = nil;

@interface AccountManager ()
- (void)sendLoginRequest;
- (void)sendTokenRefreshRequest;
- (void)sendUserInfoRequest;
- (void)showFirstRunViewController;
- (void)refreshTimerFired:(NSTimer*)theTimer;
- (void)storeCurrentUser:(User*)user;
- (void)storeOAuthToken:(OAuthToken*)token;
- (void)appDidBecomeActive:(NSNotification*)notification;

@property (nonatomic, retain) UINavigationController* navController;
@property (nonatomic, retain) FirstRunViewController* firstRunViewController;
@end

@implementation AccountManager

@synthesize authToken = authToken_;
@synthesize currentUser = currentUser_;
@synthesize delegate = delegate_;
@synthesize authenticated = authenticated_;
@synthesize navController = navController_;
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
        coldLaunch_ = YES;
        passwordKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kPasswordKeychainItemID];
        accessTokenKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kAccessTokenKeychainItemID];
        refreshTokenKeychainItem_ = [[KeychainItemWrapper alloc] initWithIdentifier:kRefreshTokenKeychainItemID];
        oAuthRequestQueue_ = [[RKRequestQueue alloc] init];
        oAuthRequestQueue_.requestTimeout = 30;
        oAuthRequestQueue_.delegate = self;
        oAuthRequestQueue_.concurrentRequestsLimit = 1;
        [oAuthRequestQueue_ start];
        [[NSNotificationCenter defaultCenter] addObserver:self
                                                 selector:@selector(appDidBecomeActive:)
                                                     name:UIApplicationDidBecomeActiveNotification
                                                   object:nil];
    }
    return self;
}

- (void)refreshToken {
    [self sendTokenRefreshRequest];
}

- (void)showFirstRunViewController {
    // TODO(auth): Cancel requests from shared queue as well.
    [oAuthRequestQueue_ cancelAllRequests];
    
    self.firstRunViewController = [[[FirstRunViewController alloc] initWithNibName:@"FirstRunViewController" bundle:nil] autorelease];
    firstRunViewController_.delegate = self;
    
    self.navController = [[[UINavigationController alloc] initWithRootViewController:self.firstRunViewController] autorelease];
    self.navController.navigationBarHidden = YES;
    
    [[Util sharedNavigationController] presentModalViewController:self.navController animated:NO];
}

- (void)authenticate {
    NSDate* tokenExpirationDate = [[NSUserDefaults standardUserDefaults] objectForKey:kTokenExpirationUserDefaultsKey];
    // Fresh install.
    if (!tokenExpirationDate) {
        [[UIApplication sharedApplication] unregisterForRemoteNotifications];
        [GTMOAuthViewControllerTouch removeParamsFromKeychainForName:kKeychainTwitterToken];
        [passwordKeychainItem_ resetKeychainItem];
        [self performSelector:@selector(showFirstRunViewController) withObject:nil afterDelay:0];
        return;
    }
    
    NSString* screenName = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
    if (screenName.length > 0) {
        self.currentUser = [User objectWithPredicate:[NSPredicate predicateWithFormat:@"screenName == %@", screenName]];
    } else {
        [self performSelector:@selector(showFirstRunViewController) withObject:nil afterDelay:0];
        return;
    }
    NSString* accessToken = [accessTokenKeychainItem_ objectForKey:(id)kSecValueData];
    NSString* refreshToken = [refreshTokenKeychainItem_ objectForKey:(id)kSecValueData];
    if (!(accessToken && refreshToken)) {
        [self sendLoginRequest];
        return;
    }
    if (coldLaunch_) {
        self.authToken = [[[OAuthToken alloc] init] autorelease];
        self.authToken.accessToken = accessToken;
        self.authToken.refreshToken = refreshToken;
        
        NSTimeInterval timeUntilTokenRefresh = [tokenExpirationDate timeIntervalSinceNow];
        if (timeUntilTokenRefresh <= 0) {
            [self sendTokenRefreshRequest];
            [self sendUserInfoRequest];
            [self.delegate accountManagerDidAuthenticate];
            return;
        }
        oauthRefreshTimer_ = [NSTimer scheduledTimerWithTimeInterval:timeUntilTokenRefresh
                                                              target:self
                                                            selector:@selector(refreshTimerFired:)
                                                            userInfo:nil
                                                             repeats:YES];
        [self sendUserInfoRequest];
        authenticated_ = YES;
        [self.delegate accountManagerDidAuthenticate];
        coldLaunch_ = NO;
    }
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
    if ([objectLoader.response isUnauthorized] &&
        [objectLoader.resourcePath rangeOfString:kUserLookupPath].location != NSNotFound) {
        [self refreshToken];
        return;
    }
    
    if ([objectLoader.response isUnauthorized] &&
        [objectLoader.resourcePath rangeOfString:kLoginPath].location != NSNotFound) {
        if (firstRunViewController_) {
            [self.firstRunViewController signInFailed:@"The username or password you entered is incorrect."];
        } else {
            [self performSelector:@selector(logout) withObject:nil afterDelay:0];
        }
    } else if ([objectLoader.resourcePath rangeOfString:kRefreshPath].location != NSNotFound) {
        [self sendLoginRequest];
    } else if ([objectLoader.resourcePath rangeOfString:kRegisterPath].location != NSNotFound) {
        [self.firstRunViewController signUpFailed:nil];
    }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
    // User information request.
    if ([object isKindOfClass:[User class]]) {
        [self storeCurrentUser:object];
        if (firstInstall_) {
            [self.firstRunViewController signUpSuccess];
            firstInstall_ = NO;
        }
        return;
    } else if ([objectLoader.resourcePath rangeOfString:kLoginPath].location != NSNotFound) {
        // Simple log in: store the OAuth token.
        self.firstRunViewController.delegate = nil;
        [[Util sharedNavigationController] dismissModalViewControllerAnimated:YES];
        self.firstRunViewController = nil;
        [self storeOAuthToken:[object objectForKey:@"token"]];
        User* user = [object objectForKey:@"user"];
        [passwordKeychainItem_ setObject:user.screenName forKey:(id)kSecAttrAccount];
        [self sendUserInfoRequest];
    } else if ([objectLoader.resourcePath rangeOfString:kRefreshPath].location != NSNotFound) {
        [self storeOAuthToken:object];
    } else if ([objectLoader.resourcePath rangeOfString:kRegisterPath].location != NSNotFound) {
        // Registering a new user.
        [self storeOAuthToken:[object objectForKey:@"token"]];
        [self sendUserInfoRequest];
        firstInstall_ = YES;
    }
    
    if (coldLaunch_) {
        authenticated_ = YES;
        [self.delegate accountManagerDidAuthenticate];
        coldLaunch_ = NO;
    }
}

- (void)sendLoginRequest {
    RKObjectManager* objectManager = [RKObjectManager sharedManager];
    RKObjectMapping* oauthMapping = [objectManager.mappingProvider mappingForKeyPath:@"UserAndToken"];
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
    RKObjectManager* objectManager = [RKObjectManager sharedManager];
    RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
    NSString* username = [passwordKeychainItem_ objectForKey:(id)kSecAttrAccount];
    RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath delegate:self];
    objectLoader.objectMapping = userMapping;
    objectLoader.params = [NSDictionary dictionaryWithKeysAndObjects:@"screen_name", username, nil];
    [objectLoader send];
}

- (void)refreshTimerFired:(NSTimer*)theTimer {
    [self sendTokenRefreshRequest];
}

- (void)storeCurrentUser:(User*)user {
    self.currentUser = user;
    [[NSNotificationCenter defaultCenter] postNotificationName:kCurrentUserHasUpdatedNotification
                                                        object:self];
}

- (void)storeOAuthToken:(OAuthToken*)token {
    [refreshTokenKeychainItem_ setObject:@"RefreshToken" forKey:(id)kSecAttrAccount];
    [refreshTokenKeychainItem_ setObject:token.refreshToken forKey:(id)kSecValueData];
    self.authToken = token;
    
    [refreshTokenKeychainItem_ setObject:@"AccessToken" forKey:(id)kSecAttrAccount];
    [accessTokenKeychainItem_ setObject:token.accessToken forKey:(id)kSecValueData];
    
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

- (void)viewController:(FirstRunViewController*)viewController
willCreateUserWithName:(NSString*)name
              username:(NSString*)handle
              password:(NSString*)password
                 email:(NSString*)email
          profileImage:(UIImage*)image
           phoneNumber:(NSString*)number {
    NSString* failedReason = nil;
    if (!name.length) {
        failedReason = @"Please fill out the 'full name' field.";
    } else if (!handle.length) {
        failedReason = @"Please enter a username.";
    } else if (!password.length) {
        failedReason = @"Please enter a password.";
    } else if (!email.length) {
        failedReason = @"Please enter your desired email address.";
    }
    if (failedReason)
        return [self.firstRunViewController signUpFailed:failedReason];
    
    [passwordKeychainItem_ setObject:handle forKey:(id)kSecAttrAccount];
    [passwordKeychainItem_ setObject:password forKey:(id)kSecValueData];
    
    RKObjectManager* manager = [RKObjectManager sharedManager];
    RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"UserAndToken"];
    RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kRegisterPath
                                                          delegate:self];
    loader.method = RKRequestMethodPOST;
    loader.objectMapping = mapping;
    
    // Don't pass an empty string as a phone number.
    if (![number length])
        number = nil;
    
    RKParams* params = [RKParams paramsWithDictionary:
                        [NSDictionary dictionaryWithObjectsAndKeys:name, @"name",
                         email, @"email",
                         handle, @"screen_name",
                         password, @"password",
                         kClientID, @"client_id",
                         kClientSecret, @"client_secret",
                         number, @"phone",  // Last so it can be nil.
                         nil]];
    
    if (image) {
        NSData* imageData = UIImageJPEGRepresentation(image, 0.8);
        [params setData:imageData MIMEType:@"image/jpeg" forParam:@"profile_image"];
    }
    loader.params = params;
    
    [oAuthRequestQueue_ addRequest:loader];
}


- (void)createAccountWithFacebook:(NSString*)name
                       screenname:(NSString*)screenname
                        userToken:(NSString*)userToken 
                            email:(NSString*)email {
    [self createAccountWithFacebook:name
                         screenname:screenname
                          userToken:userToken
                              email:email
                              phone:nil
                       profileImage:nil];
}

- (void)createAccountWithFacebook:(NSString*)name
                       screenname:(NSString*)screenname
                        userToken:(NSString*)userToken 
                            email:(NSString*)email 
                            phone:(NSString*)phone 
                     profileImage:(NSString*)profileImage {
    [passwordKeychainItem_ setObject:screenname forKey:(id)kSecAttrAccount];
    [passwordKeychainItem_ setObject:@"password" forKey:(id)kSecValueData];
    
    RKObjectManager* manager = [RKObjectManager sharedManager];
    RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"UserAndToken"];
    RKObjectLoader* loader = [manager objectLoaderWithResourcePath:@"/account/create/facebook.json"
                                                          delegate:self];
    loader.method = RKRequestMethodPOST;
    loader.objectMapping = mapping;
    
    RKParams* params = [RKParams paramsWithDictionary:
                        [NSDictionary dictionaryWithObjectsAndKeys:name, @"name",
                         email, @"email",
                         screenname, @"screen_name",
                         userToken, @"user_token",
                         kClientID, @"client_id",
                         kClientSecret, @"client_secret",
                         nil]];
    if (phone) {
        [params setValue:phone forParam:@"phone"];
    }
    loader.params = params;
    
    [oAuthRequestQueue_ addRequest:loader];
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
        if (request.isGET && [request.URL isKindOfClass:[RKURL class]]) {
            request.resourcePath = [request.resourcePath appendQueryParams:params];
            request.params = nil;
        }
    }
}

- (void)requestQueueDidFinishLoading:(RKRequestQueue*)queue {
    if ([RKClient sharedClient].requestQueue.count == 0 && oAuthRequestQueue_.count == 0) {
        [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    }
    if (queue == oAuthRequestQueue_ && queue.count == 0) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didLoadResponse:(RKResponse*)response {
    if (queue == oAuthRequestQueue_) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)requestQueue:(RKRequestQueue*)queue didCancelRequest:(RKRequest*)request {
    if (queue == oAuthRequestQueue_)
        [RKClient sharedClient].requestQueue.suspended = NO;
}

- (void)requestQueue:(RKRequestQueue*)queue didFailRequest:(RKRequest*)request withError:(NSError*)error {
    if (queue == oAuthRequestQueue_) {
        [RKClient sharedClient].requestQueue.suspended = NO;
    }
}

- (void)appDidBecomeActive:(NSNotification*)notification {
    if (oAuthRequestQueue_.count == 0)
        [RKClient sharedClient].requestQueue.suspended = NO;
}

#pragma mark - Logout stuff.

- (void)logout {
    [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
    // Remove Facebook credentials.
    [[SocialManager sharedManager] signOutOfFacebook:NO];
    [[SocialManager sharedManager] signOutOfTwitter:NO];
    
    [oAuthRequestQueue_ cancelAllRequests];
    [[RKClient sharedClient].requestQueue cancelAllRequests];
    [passwordKeychainItem_ resetKeychainItem];
    [accessTokenKeychainItem_ resetKeychainItem];
    [refreshTokenKeychainItem_ resetKeychainItem];
    [GTMOAuthViewControllerTouch removeParamsFromKeychainForName:kKeychainTwitterToken];
    [[UIApplication sharedApplication] unregisterForRemoteNotifications];
    [[NSUserDefaults standardUserDefaults] removePersistentDomainForName:[[NSBundle mainBundle] bundleIdentifier]];
    self.currentUser = nil;
    self.authToken = nil;
    NSString* baseURL = [RKClient sharedClient].baseURL;
    [RKClient sharedClient].baseURL = nil;
    [[RKObjectManager sharedManager].objectStore deletePersistantStore];
    NSFileManager* fm = [NSFileManager defaultManager];
    NSURL* directoryURL = [[fm URLsForDirectory:NSCachesDirectory inDomains:NSUserDomainMask] lastObject];
    NSError* error = nil;
    for (NSString* file in [fm contentsOfDirectoryAtPath:directoryURL.path error:&error]) {
        BOOL success = [fm removeItemAtURL:[directoryURL URLByAppendingPathComponent:file] error:&error];
        if (!success || error) {
            NSLog(@"Deleting stuff failed: %@", error);
        }
    }
    authenticated_ = NO;
    coldLaunch_ = YES;
    [[NSNotificationCenter defaultCenter] postNotificationName:kUserHasLoggedOutNotification
                                                        object:self];
    [RKClient sharedClient].baseURL = baseURL;
    [self authenticate];
}

@end

