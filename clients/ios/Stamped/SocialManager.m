//
//  SocialManager.m
//  Stamped
//
//  Created by Jake Zien on 11/14/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <Accounts/Accounts.h>
#import <Twitter/Twitter.h>

#import "AccountManager.h"
#import "SocialManager.h"
#import "GTMOAuthAuthentication.h"
#import "STOAuthViewController.h"
#import "StampedAppDelegate.h"
#import "Util.h"
#import "Stamp.h"
#import "Entity.h"
#import "FacebookUser.h"
#import "OAuth+Additions.h"
#import "TwitterUser.h"
#import "TWSignedRequest.h"
#import "User.h"

static SocialManager* sharedManager_ = nil;

static NSString* const kiOS5TwitterAccountIdentifier = @"kiOS5TwitterAccountIdentifier";
static NSString* const kTwitterUsername = @"TwitterUsername";

static NSString* const kTwitterBaseURI = @"http://api.twitter.com/1/";
static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kTwitterSignOutURI = @"/account/end_session.json";
static NSString* const kTwitterUpdateStatusPath = @"/statuses/update.json";
static NSString* const kTwitterUserLookupPath = @"/users/lookup.json";
static NSString* const kTwitterFullRequestTokenPath = @"https://api.twitter.com/oauth/request_token";
static NSString* const kTwitterFullAuthTokenPath = @"https://api.twitter.com/oauth/access_token";

static NSString* const kFacebookFriendsURI = @"/me/friends?limit=0";
static NSString* const kFacebookAppID = @"297022226980395";
static NSString* const kStampedTwitterLinkPath = @"/account/linked/twitter/update.json";
static NSString* const kStampedTwitterRemovePath = @"/account/linked/twitter/remove.json";
static NSString* const kStampedFacebookLinkPath = @"/account/linked/facebook/update.json";
static NSString* const kStampedFacebookRemovePath = @"/account/linked/facebook/remove.json";
static NSString* const kStampedLogoURLPath = @"http://static.stamped.com/logos/";

NSString* const kStampedFindFacebookFriendsPath = @"/users/find/facebook.json";
NSString* const kStampedFindTwitterFriendsPath = @"/users/find/twitter.json";
NSString* const kSocialNetworksChangedNotification = @"kSocialNetworksChangedNotification";
NSString* const kTwitterFriendsChangedNotification = @"kTwitterFriendsChangedNotification";
NSString* const kTwitterFriendsNotOnStampedReceivedNotification = @"kTwitterFriendsNotOnStampedReceivedNotification";
NSString* const kFacebookFriendsChangedNotification = @"kFacebookFriendsChangedNotification"; 


@interface SocialManager ()

// iOS5 Accounts manager.
@property (nonatomic, retain) ACAccountStore* accountStore;
@property (nonatomic, retain) Facebook* facebookClient;
@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;
@property (nonatomic, copy) NSArray* twitterFriends;
@property (nonatomic, retain) NSMutableSet* twitterIDsNotUsingStamped;
@property (nonatomic, copy) NSArray* facebookFriends;
@property (nonatomic, assign) BOOL isSigningInToTwitter;
@property (nonatomic, assign) BOOL isSigningInToFacebook;

- (void)showTwitterAccountChoices:(NSArray*)accounts;
- (void)accountWasAuthorized:(ACAccount*)account;
- (void)storeMainTwitterAccountAs:(ACAccount*)account;
- (void)didReceiveTwitterFriends:(NSDictionary*)friends;
- (void)didReceiveTwitterFriendsNotUsingStamped:(NSArray*)friends;
- (void)displayNoAccountsAlert;

- (void)checkForEndlessSignIn:(NSNotification*)note;
- (void)requestTwitterUser;
- (void)requestTwitterFriends:(NSString*)userIDString;
- (void)removeTwitterCredentials;
- (void)removeFacebookCredentials;
- (void)requestStampedLinkTwitter:(NSString*)username userID:(NSString*)userID token:(NSString*)token secret:(NSString*)tokenSecret;
- (void)requestStampedUnlinkTwitter;
- (void)requestStampedLinkFacebook:(NSString*)name userID:(NSString*)userID token:(NSString*)token;
- (void)requestStampedUnlinkFacebook;
- (void)requestStampedFriendsFromFacebook:(NSString*)accessToken;
- (void)requestStampedFriendsFromTwitter;
- (void)sendStampedTwitterFriendsRequestWithToken:(NSString*)token secret:(NSString*)tokenSecret;
- (void)requestTwitterUsersNotUsingStamped;

- (GTMOAuthAuthentication*)createAuthentication;
- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error;

@end

@implementation SocialManager

@synthesize accountStore = accountStore_;
@synthesize facebookClient = facebookClient_;
@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;
@synthesize twitterFriends = twitterFriends_;
@synthesize twitterFriendsNotUsingStamped = twitterFriendsNotUsingStamped_;
@synthesize twitterIDsNotUsingStamped = twitterIDsNotUsingStamped_;
@synthesize facebookFriends = facebookFriends_;
@synthesize facebookFriendsNotUsingStamped = facebookFriendsNotUsingStamped_;
@synthesize isSigningInToTwitter = isSigningInToTwitter_;
@synthesize isSigningInToFacebook = isSigningInToFacebook_;

#pragma mark - Singleton / lifecycle.

+ (SocialManager*)sharedManager {
  if (sharedManager_ == nil)
    sharedManager_ = [[super allocWithZone:NULL] init];
  
  return sharedManager_;
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

- (id)init {
  self = [super init];
  if (self) {
    self.accountStore = [[ACAccountStore alloc] init];
    self.facebookClient = [[Facebook alloc] initWithAppId:kFacebookAppID andDelegate:nil];
    self.twitterClient = [RKClient clientWithBaseURL:kTwitterBaseURI];
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(checkForEndlessSignIn:)
                                                 name:UIApplicationDidBecomeActiveNotification
                                               object:nil];
  }
  return self;
}

#pragma mark - Public.

- (BOOL)hasiOS5Twitter {
  return (accountStore_ != nil);
}

- (BOOL)isSignedInToTwitter {
  if (accountStore_) {
    NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
    ACAccount* account = [accountStore_ accountWithIdentifier:identifier];
    return account != nil;
  }

  GTMOAuthAuthentication* auth = [self createAuthentication];
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    self.authentication = auth;
    return YES;
  }
  return NO;
}

- (BOOL)isSignedInToFacebook {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"])
    self.facebookClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
  if ([defaults objectForKey:@"FBExpirationDateKey"])
    self.facebookClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  
  return self.facebookClient.isSessionValid ? YES : NO;
}

- (void)refreshStampedFriendsFromTwitter {
  self.twitterFriends = nil;
  self.twitterIDsNotUsingStamped = nil;
  self.twitterFriendsNotUsingStamped = nil;
  [self requestTwitterUser];
}

- (void)refreshStampedFriendsFromFacebook {
  [self.facebookClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
}

#pragma mark - Twitter.

- (void)signInToTwitter:(UINavigationController*)navigationController {
  if (accountStore_) {
    ACAccountType* accountType = [accountStore_ accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
    if (![self isSignedInToTwitter] || !accountType.accessGranted) {
      SocialManager* manager = self;
      [accountStore_ requestAccessToAccountsWithType:accountType
                               withCompletionHandler:^(BOOL granted, NSError* error) {
                                 if (granted) {
                                   NSArray* accounts = [accountStore_ accountsWithAccountType:accountType];
                                   if (accounts.count == 0) {
                                     [manager performSelectorOnMainThread:@selector(displayNoAccountsAlert)
                                                               withObject:nil
                                                            waitUntilDone:NO];
                                   } else if (accounts.count == 1) {
                                     ACAccount* account = accounts.lastObject;
                                     [manager performSelectorOnMainThread:@selector(accountWasAuthorized:)
                                                               withObject:account
                                                            waitUntilDone:NO];
                                   } else if (accounts.count > 1) {
                                     [manager performSelectorOnMainThread:@selector(showTwitterAccountChoices:)
                                                               withObject:accounts
                                                            waitUntilDone:NO];
                                   }
                                 }
                               }];
    }
  } else {
    GTMOAuthAuthentication* auth = [self createAuthentication];
    if (auth == nil)
      NSAssert(NO, @"A valid consumer key and consumer secret are required for signing in to Twitter");

    isSigningInToTwitter_ = YES;

    STOAuthViewController* authVC =
        [[STOAuthViewController alloc] initWithScope:kTwitterScope
                                            language:nil
                                     requestTokenURL:[NSURL URLWithString:kTwitterRequestTokenURL]
                                   authorizeTokenURL:[NSURL URLWithString:kTwitterAuthorizeURL]
                                      accessTokenURL:[NSURL URLWithString:kTwitterAccessTokenURL]
                                      authentication:auth
                                      appServiceName:kKeychainTwitterToken
                                            delegate:self
                                    finishedSelector:@selector(viewController:finishedWithAuth:error:)];
    [authVC setBrowserCookiesURL:[NSURL URLWithString:@"http://api.twitter.com/"]];
    
    [navigationController pushViewController:authVC animated:YES];
    [authVC release];
  }
}

- (void)displayNoAccountsAlert {
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"No Twitter Accounts Found"
                                                   message:@"Log in or create an account in the Settings app"
                                                  delegate:self
                                         cancelButtonTitle:@"Cancel"
                                         otherButtonTitles:@"Settings", nil] autorelease];
  [alert show];
}

#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView*)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == alertView.cancelButtonIndex)
    return;

  [[UIApplication sharedApplication] openURL:[NSURL URLWithString:@"prefs:root=TWITTER"]];
}

- (void)accountWasAuthorized:(ACAccount*)account {
  [self storeMainTwitterAccountAs:account];
  [self requestTwitterUser];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:nil];
}

- (void)storeMainTwitterAccountAs:(ACAccount*)account {
  [[NSUserDefaults standardUserDefaults] setObject:account.identifier forKey:kiOS5TwitterAccountIdentifier];
  [[NSUserDefaults standardUserDefaults] synchronize];
}

- (void)showTwitterAccountChoices:(NSArray*)accounts {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:@"Which Twitter account would you would like to use?"
                                                      delegate:self
                                             cancelButtonTitle:nil
                                        destructiveButtonTitle:nil
                                             otherButtonTitles:nil] autorelease];
  for (ACAccount* account in accounts)
    [sheet addButtonWithTitle:account.username];

  sheet.cancelButtonIndex = [sheet addButtonWithTitle:@"Cancel"];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  UIWindow* win = [(StampedAppDelegate*)[[UIApplication sharedApplication] delegate] window];
  [sheet showInView:win];
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == actionSheet.cancelButtonIndex) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:nil];
    return;
  }

  NSString* username = [actionSheet buttonTitleAtIndex:buttonIndex];
  ACAccountType* accountType = [accountStore_ accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
  NSArray* accounts = [accountStore_ accountsWithAccountType:accountType];
  ACAccount* account = nil;
  for (ACAccount* a in accounts) {
    if ([a.username isEqualToString:username]) {
      account = a;
      break;
    }
  }
  [self storeMainTwitterAccountAs:account];
  [self requestTwitterUser];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:nil];
}

- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error {  
  if (error) {
    NSLog(@"GTMOAuth error = %@", error);
    [self signOutOfTwitter:YES];
    return;
  }
  self.authentication = auth;
  if (!self.twitterClient)
    self.twitterClient = [RKClient clientWithBaseURL:kTwitterBaseURI];
  // Signed in, but the process isn't complete until we link the user on the backend.
  [self requestTwitterUser];
}

- (void)signOutOfTwitter:(BOOL)unlink {
  if (![self hasiOS5Twitter]) {
    isSigningInToTwitter_ = NO;
    RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterSignOutURI delegate:self];
    request.method = RKRequestMethodPOST;
    [request prepareURLRequest];
    [self.authentication authorizeRequest:request.URLRequest];
    [request send];
  }

  // Unlink the Twitter info from the user's account on the backend.
  if (unlink)
    [self requestStampedUnlinkTwitter];
  [self removeTwitterCredentials];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

- (void)removeTwitterCredentials {
  [GTMOAuthViewControllerTouch removeParamsFromKeychainForName:kKeychainTwitterToken];
  [[NSUserDefaults standardUserDefaults] removeObjectForKey:kTwitterUsername];
  [[NSUserDefaults standardUserDefaults] removeObjectForKey:kiOS5TwitterAccountIdentifier];
  [[NSUserDefaults standardUserDefaults] synchronize];
}

- (void)requestTwitterPostWithStamp:(Stamp*)stamp {
  NSString* blurb = [NSString stringWithFormat:@"%@. \u201c%@\u201d", stamp.entityObject.title, stamp.blurb];
  if (stamp.blurb.length == 0)
    blurb = [stamp.entityObject.title stringByAppendingString:@"."];

  BOOL hasImage = stamp.imageURL != nil;
  
  NSString* substring = [blurb substringToIndex:MIN(blurb.length, hasImage ? 98 : 104)];
  if (blurb.length > substring.length)
    blurb = [substring stringByAppendingString:@"..."];
  
  NSString* initial = hasImage ? @"Stamped [pic]:" : @"Stamped:";
  // Stamped ([pic]): [blurb] [link]
  NSString* tweet = [NSString stringWithFormat:@"%@ %@ %@", initial, blurb, stamp.URL];
  [self requestTwitterPostWithStatus:tweet];
}

- (void)requestTwitterPostWithStatus:(NSString*)status {
  if ([self hasiOS5Twitter]) {
    NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
    ACAccount* account = [accountStore_ accountWithIdentifier:identifier];
    NSDictionary* params = [NSDictionary dictionaryWithObject:status forKey:@"status"];
    NSURL* url = [NSURL URLWithString:@"http://api.twitter.com/1/statuses/update.json"];
    TWRequest* request = [[[TWRequest alloc] initWithURL:url parameters:params requestMethod:TWRequestMethodPOST] autorelease];    
    request.account = account;
    [request performRequestWithHandler:^(NSData* responseData, NSHTTPURLResponse* urlResponse, NSError* error) {}];
  } else if (self.authentication) {
    RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterUpdateStatusPath
                                                            delegate:nil];
    request.method = RKRequestMethodPOST;
    [request.URLRequest setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"];
    [request.URLRequest setHTTPMethod:@"POST"];
    status = [status stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
    status = [status stringByReplacingOccurrencesOfString:@"&" withString:@"%26"];  // FUCK YOU.
    status = [status stringByReplacingOccurrencesOfString:@"+" withString:@"%2B"];  // FUCK YOU.
    NSString* body = [NSString stringWithFormat:@"status=%@", status];
    [request.URLRequest setHTTPBody:[body dataUsingEncoding:NSUTF8StringEncoding]];
    [self.authentication authorizeRequest:request.URLRequest];
    [request send];
  }
}

- (GTMOAuthAuthentication*)createAuthentication {
  NSString* myConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
  NSString* myConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";
  
  if ([myConsumerKey length] == 0 || [myConsumerSecret length] == 0) {
    return nil;
  }
  
  GTMOAuthAuthentication* auth;
  auth = [[[GTMOAuthAuthentication alloc] initWithSignatureMethod:kGTMOAuthSignatureMethodHMAC_SHA1
                                                      consumerKey:myConsumerKey
                                                       privateKey:myConsumerSecret] autorelease];
  [auth setServiceProvider:@"Twitter"];
  [auth setCallback:kOAuthCallbackURL];
  return auth;
}

- (NSString*)twitterUsername {
  return [[NSUserDefaults standardUserDefaults] objectForKey:kTwitterUsername];
}

- (NSString*)twitterProfileImageURL {
  if (!self.twitterUsername)
    return nil;
  
  return [NSString stringWithFormat:@"https://api.twitter.com/1/users/profile_image?screen_name=%@&size=bigger", self.twitterUsername];
}

- (NSString*)largeTwitterProfileImageURL {
  if (!self.twitterUsername)
    return nil;
  
  return [NSString stringWithFormat:@"https://api.twitter.com/1/users/profile_image?screen_name=%@&size=reasonably_small", self.twitterUsername];
}

- (void)requestTwitterUser {
  if ([self hasiOS5Twitter]) {
    TWSignedRequest* signedRequest = [[[TWSignedRequest alloc] initWithURL:[NSURL URLWithString:kTwitterFullRequestTokenPath]
                                                                parameters:[NSDictionary dictionaryWithObject:@"reverse_auth" forKey:@"x_auth_mode"]
                                                             requestMethod:TWSignedRequestMethodPOST] autorelease];
    [signedRequest performRequestWithHandler:^(NSData* data, NSURLResponse* response, NSError* error) {
      if (data == nil) {
        NSLog(@"Problem getting data: %@", error.localizedDescription);
      } else {
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
          NSString* signedReverseAuthSignature = [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] autorelease];
          NSDictionary* step2Params = [NSDictionary dictionaryWithObjectsAndKeys:[TWSignedRequest consumerKey], @"x_reverse_auth_target",
                                       signedReverseAuthSignature, @"x_reverse_auth_parameters", nil];
          NSURL* authTokenURL = [NSURL URLWithString:kTwitterFullAuthTokenPath];
          TWRequest* step2Request = [[[TWRequest alloc] initWithURL:authTokenURL parameters:step2Params requestMethod:TWRequestMethodPOST] autorelease];
          NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
          [step2Request setAccount:[accountStore_ accountWithIdentifier:identifier]];
          [step2Request performRequestWithHandler:^(NSData *responseData, NSHTTPURLResponse *urlResponse, NSError *error) {
            
            //  Something went wrong
            if (responseData == nil) {
              NSLog(@"Error occurred in Step 2 of Twitter reverse Auth");
            } else {
              NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
              ACAccount* account = [accountStore_ accountWithIdentifier:identifier];
              NSString* userID = [account valueForKeyPath:@"properties.user_id"];
              NSString* responseStr = [[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding];
              NSDictionary* responseDictionary = [NSURL ab_parseURLQueryString:responseStr];
              [self requestStampedLinkTwitter:account.username
                                       userID:userID 
                                        token:[responseDictionary objectForKey:@"oauth_token"]
                                       secret:[responseDictionary objectForKey:@"oauth_token_secret"]];
              [self requestTwitterFriends:userID];
            }
          }];
        });
      }
    }];
  } else {  
    if (!self.twitterClient)
      self.twitterClient = [RKClient clientWithBaseURL:kTwitterBaseURI];

    RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:self];
    request.cachePolicy = RKRequestCachePolicyNone;
    [request prepareURLRequest];
    [self.authentication authorizeRequest:request.URLRequest];
    [request send];
  }
}

- (void)requestTwitterFriends:(NSString*)userIDString {
  if ([self hasiOS5Twitter]) {
    NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
    ACAccount* account = [accountStore_ accountWithIdentifier:identifier];
    NSURL* url = [NSURL URLWithString:@"http://api.twitter.com/1/friends/ids.json"];
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:@"-1", @"cursor", nil];
    TWRequest* request = [[[TWRequest alloc] initWithURL:url parameters:params requestMethod:TWRequestMethodGET] autorelease];
    request.account = account;

    [request performRequestWithHandler:^(NSData* responseData, NSHTTPURLResponse* urlResponse, NSError* error) {
      if ([urlResponse statusCode] == 200) {
        NSError* error = nil;
        NSDictionary* friendsObject = [NSJSONSerialization JSONObjectWithData:responseData options:0 error:&error];
        if (friendsObject)
          [self performSelectorOnMainThread:@selector(didReceiveTwitterFriends:) withObject:friendsObject waitUntilDone:NO];
      }
    }];
  } else {
    if (!self.twitterClient)
      self.twitterClient = [RKClient clientWithBaseURL:kTwitterBaseURI];
    NSDictionary* params = [NSDictionary dictionaryWithObjectsAndKeys:@"-1", @"cursor", userIDString, @"user_id", nil];
    NSString* path = [kTwitterFriendsURI appendQueryParams:params];
    RKRequest* request = [self.twitterClient requestWithResourcePath:path delegate:self];
    [self.authentication authorizeRequest:request.URLRequest];
    [request send];
  }
}

- (void)didReceiveTwitterFriends:(NSDictionary*)friends {
  self.twitterIDsNotUsingStamped = [NSMutableSet setWithArray:[friends objectForKey:@"ids"]];
  [self requestStampedFriendsFromTwitter];
}

#pragma mark - Facebook.

- (NSString*)facebookProfileImageURL {
  NSString* facebookID = [[NSUserDefaults standardUserDefaults] objectForKey:@"FBID"];
  if (!facebookID)
    return nil;

  return [NSString stringWithFormat:@"https://graph.facebook.com/%@/picture", facebookID];
}

- (NSString*)facebookName {
  return [[NSUserDefaults standardUserDefaults] objectForKey:@"FBName"];
}

- (void)signInToFacebook {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.facebookClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.facebookClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  if (!self.facebookClient.isSessionValid) {
    self.facebookClient.sessionDelegate = self;
    isSigningInToFacebook_ = YES;
    [self.facebookClient authorize:[NSArray arrayWithObjects:@"offline_access", @"publish_stream", nil]];
  }
}

- (void)signOutOfFacebook:(BOOL)unlink {
  isSigningInToFacebook_ = NO;
  [self.facebookClient logout];
  [self removeFacebookCredentials];
  if (unlink)
    [self requestStampedUnlinkFacebook];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

- (void)removeFacebookCredentials {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"]) {
    [defaults removeObjectForKey:@"FBAccessTokenKey"];
    [defaults removeObjectForKey:@"FBExpirationDateKey"];
    [defaults removeObjectForKey:@"FBName"];
    [defaults removeObjectForKey:@"FBID"];
    [defaults synchronize];
    
    // Nil out the session variables to prevent
    // the app from thinking there is a valid session
    if (nil != self.facebookClient.accessToken) {
      self.facebookClient.accessToken = nil;
    }
    if (nil != self.facebookClient.expirationDate) {
      self.facebookClient.expirationDate = nil;
    }
  }
}

- (void)requestFacebookPostWithStamp:(Stamp*)stamp {
  NSString* fbID = [[NSUserDefaults standardUserDefaults] objectForKey:@"FBID"];
  if (!fbID)
    return;
  
  if (self.facebookClient.isSessionValid) {
    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                   kFacebookAppID, @"app_id",
                                   stamp.URL, @"link",
                                   stamp.entityObject.title, @"name", nil];
    NSString* photoURL = [NSString stringWithFormat:@"%@%@-%@%@", kStampedLogoURLPath, stamp.user.primaryColor, stamp.user.secondaryColor, @"-logo-195x195.png"];
    [params setObject:photoURL forKey:@"picture"];
    
    if (stamp.blurb.length > 0)
      [params setObject:stamp.blurb forKey:@"message"];
    
    [self.facebookClient requestWithGraphPath:[fbID stringByAppendingString:@"/feed"]
                                    andParams:params
                                andHttpMethod:@"POST"
                                  andDelegate:nil];
  }
}

- (NSString*)stampedLogoImageURL {
  User* currentUser = [AccountManager sharedManager].currentUser;
  return [NSString stringWithFormat:@"%@%@-%@%@", kStampedLogoURLPath, currentUser.primaryColor, currentUser.secondaryColor, @"-logo-195x195.png"];
}

- (void)requestFacebookPostInviteToFacebookID:(NSString*)facebookID {
  if (!self.facebookClient.isSessionValid)
    return;

  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                    kFacebookAppID, @"app_id",
                                    @"http://stamped.com", @"link",
                                    @"Stamped", @"name", nil];
  [params setObject:self.stampedLogoImageURL forKey:@"picture"];
  [params setObject:@"Hey, I think you have great taste, so join me on Stamped and share the things you like best."
             forKey:@"message"];

  [self.facebookClient requestWithGraphPath:[facebookID stringByAppendingString:@"/feed"]
                                  andParams:params
                              andHttpMethod:@"POST"
                                andDelegate:nil];
}

- (BOOL)handleOpenURLFromFacebook:(NSURL*)URL {
  if (self.facebookClient)
    return [self.facebookClient handleOpenURL:URL];

  return NO;
}

// FBSessionDelegate methods.

- (void)fbDidLogin {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:self.facebookClient.accessToken forKey:@"FBAccessTokenKey"];
  [defaults setObject:self.facebookClient.expirationDate forKey:@"FBExpirationDateKey"];
  [defaults synchronize];
  [self.facebookClient requestWithGraphPath:@"me" andDelegate:self];
}

- (void)fbDidNotLogin:(BOOL)cancelled {
  [self signOutOfFacebook:YES];
}

- (void)fbDidExtendToken:(NSString*)accessToken expiresAt:(NSDate*)expiresAt {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:accessToken forKey:@"FBAccessTokenKey"];
  [defaults setObject:expiresAt forKey:@"FBExpirationDateKey"];
  [defaults synchronize];
}

- (void)fbDidLogout {
  [self signOutOfFacebook:YES];
}

- (void)fbSessionInvalidated {
  [self signOutOfFacebook:YES];
}

// FBRequestDelegate methods.

- (void)request:(FBRequest*)request didLoad:(id)result {
  NSArray* resultData = nil;
  
  if ([result isKindOfClass:[NSArray class]])
    result = [result objectAtIndex:0];
  if ([result isKindOfClass:[NSDictionary class]]) {
    // handle callback from request for current user info.
    if ([result objectForKey:@"name"]) {
      [self requestStampedLinkFacebook:[result objectForKey:@"name"]
                                userID:[result objectForKey:@"id"]
                                 token:self.facebookClient.accessToken];
      [self.facebookClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
    }
    resultData = [result objectForKey:@"data"];
  }

  // handle callback from request for user's friends.
  if (resultData) {
    self.facebookFriendsNotUsingStamped = [NSMutableSet set];
    for (NSDictionary* friend in resultData) {
      FacebookUser* user = [[FacebookUser alloc] init];
      user.name = [friend valueForKey:@"name"];
      user.facebookID = [friend valueForKey:@"id"];
      user.profileImageURL = [NSString stringWithFormat:@"https://graph.facebook.com/%@/picture", user.facebookID];
      [facebookFriendsNotUsingStamped_ addObject:user];
      [user release];
    }

    [self requestStampedFriendsFromFacebook:self.facebookClient.accessToken];
  }
}

- (void)request:(FBRequest*)request didFailWithError:(NSError*)error {
  if (isSigningInToFacebook_)
    [self signOutOfFacebook:YES];
  if (error.code == 10000)  // WTF? This doesn't necessarily mean it should log out.
    [self signOutOfFacebook:YES];
}

#pragma mark - Stamped.

- (void)requestStampedFriendsFromFacebook:(NSString*)accessToken {
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedFindFacebookFriendsPath
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:accessToken forKey:@"facebook_token"];
  loader.objectMapping = mapping;
  [loader send];
}

- (void)requestStampedLinkFacebook:(NSString*)name userID:(NSString*)userID token:(NSString*)token {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:name forKey:@"FBName"];
  [defaults setObject:userID forKey:@"FBID"];
  [defaults synchronize];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedFacebookLinkPath delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"facebook_id", name, @"facebook_name", token, @"facebook_token", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)requestStampedUnlinkFacebook {
  // Unlink the Facebook info from the user's account on the backend.
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedFacebookRemovePath delegate:self];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)requestStampedFriendsFromTwitter {
  if ([self hasiOS5Twitter]) {
    TWSignedRequest* signedRequest = [[[TWSignedRequest alloc] initWithURL:[NSURL URLWithString:kTwitterFullRequestTokenPath]
                                                                parameters:[NSDictionary dictionaryWithObject:@"reverse_auth" forKey:@"x_auth_mode"]
                                                             requestMethod:TWSignedRequestMethodPOST] autorelease];
    [signedRequest performRequestWithHandler:^(NSData* data, NSURLResponse* response, NSError* error) {
      if (data == nil) {
        NSLog(@"Problem getting data: %@", error.localizedDescription);
      } else {
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
          NSString* signedReverseAuthSignature = [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] autorelease];
          NSDictionary* step2Params = [NSDictionary dictionaryWithObjectsAndKeys:[TWSignedRequest consumerKey], @"x_reverse_auth_target",
                                       signedReverseAuthSignature, @"x_reverse_auth_parameters", nil];
          NSURL* authTokenURL = [NSURL URLWithString:kTwitterFullAuthTokenPath];
          TWRequest* step2Request = [[[TWRequest alloc] initWithURL:authTokenURL parameters:step2Params requestMethod:TWRequestMethodPOST] autorelease];
          NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
          [step2Request setAccount:[accountStore_ accountWithIdentifier:identifier]];
          [step2Request performRequestWithHandler:^(NSData *responseData, NSHTTPURLResponse *urlResponse, NSError *error) {
            
            //  Something went wrong
            if (responseData == nil) {
              NSLog(@"Error occurred in Step 2 of Twitter reverse Auth");
            } else {
              NSString* responseStr = [[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding];
              NSDictionary* responseDictionary = [NSURL ab_parseURLQueryString:responseStr];
              [self sendStampedTwitterFriendsRequestWithToken:[responseDictionary objectForKey:@"oauth_token"]
                                                       secret:[responseDictionary objectForKey:@"oauth_token_secret"]];
            }
          }];
        });
      }
    }];
  } else if (self.authentication) {
    [self sendStampedTwitterFriendsRequestWithToken:self.authentication.token secret:self.authentication.tokenSecret];
  }
}

- (void)sendStampedTwitterFriendsRequestWithToken:(NSString*)token secret:(NSString*)tokenSecret {
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedFindTwitterFriendsPath
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObjectsAndKeys:token, @"twitter_key", tokenSecret, @"twitter_secret", nil];
  loader.objectMapping = mapping;
  [loader send];
}

- (void)requestStampedLinkTwitter:(NSString*)username userID:(NSString*)userID token:(NSString*)token secret:(NSString*)tokenSecret {
  [[NSUserDefaults standardUserDefaults] setObject:username forKey:kTwitterUsername];
  [[NSUserDefaults standardUserDefaults] synchronize];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedTwitterLinkPath
                                                               delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"twitter_id",
                                                              username, @"twitter_screen_name",
                                                              token, @"twitter_key",
                                                              tokenSecret, @"twitter_secret", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)requestStampedUnlinkTwitter {
  RKRequest* unlinkRequest = [[RKClient sharedClient] requestWithResourcePath:kStampedTwitterRemovePath delegate:self];
  unlinkRequest.method = RKRequestMethodPOST;
  [unlinkRequest send];
}

- (void)requestTwitterUsersNotUsingStamped {
  if (twitterIDsNotUsingStamped_.count == 0) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kTwitterFriendsNotOnStampedReceivedNotification object:self];
    return;
  }

  NSArray* friendIDs = [twitterIDsNotUsingStamped_.allObjects subarrayWithRange:NSMakeRange(0, MIN(twitterIDsNotUsingStamped_.count, 100))];
  NSDictionary* params = [NSDictionary dictionaryWithObject:[friendIDs componentsJoinedByString:@","] forKey:@"user_id"];
  NSString* fullTwitterUserLookupPath = @"http://api.twitter.com/1/users/lookup.json";

  if ([self hasiOS5Twitter]) {
    NSString* identifier = [[NSUserDefaults standardUserDefaults] stringForKey:kiOS5TwitterAccountIdentifier];
    ACAccount* account = [accountStore_ accountWithIdentifier:identifier];

    NSURL* url = [NSURL URLWithString:@"http://api.twitter.com/1/users/lookup.json"];
    TWRequest* request = [[[TWRequest alloc] initWithURL:url parameters:params requestMethod:TWRequestMethodGET] autorelease];    
    request.account = account;    
    [request performRequestWithHandler:^(NSData* responseData, NSHTTPURLResponse* urlResponse, NSError* error) {
      if ([urlResponse statusCode] == 200) {
        NSError* error = nil;
        NSArray* friendsObject = [NSJSONSerialization JSONObjectWithData:responseData options:0 error:&error];
        if (friendsObject)
          [self performSelectorOnMainThread:@selector(didReceiveTwitterFriendsNotUsingStamped:) withObject:friendsObject waitUntilDone:NO];
      }
    }];
  } else if (self.authentication) {
    // A full NSURL object has to be created because otherwise it will fail to append the query params
    // to the path. TODO(andybons): File a RestKit bug about this.
    NSString* path = [fullTwitterUserLookupPath appendQueryParams:params];
    RKRequest* request = [RKRequest requestWithURL:[NSURL URLWithString:path] delegate:self];
    [self.authentication authorizeRequest:request.URLRequest];
    [self.twitterClient.requestQueue addRequest:request];
  }
}

- (void)didReceiveTwitterFriendsNotUsingStamped:(NSArray*)friends {
  if (!twitterFriendsNotUsingStamped_)
    self.twitterFriendsNotUsingStamped = [NSMutableSet set];

  for (NSDictionary* friend in friends) {
    TwitterUser* user = [[TwitterUser alloc] init];
    user.name = [friend objectForKey:@"name"];
    user.screenName = [NSString stringWithFormat:@"@%@", [friend objectForKey:@"screen_name"]];
    user.profileImageURL = [friend objectForKey:@"profile_image_url"];
    user.profileImageURL  = [user.profileImageURL stringByReplacingOccurrencesOfString:@"_normal"
                                                                            withString:@"_reasonably_small"
                                                                               options:(NSCaseInsensitiveSearch | NSBackwardsSearch)
                                                                                 range:NSMakeRange(0, user.profileImageURL.length)];
    [twitterFriendsNotUsingStamped_ addObject:user];
    [user release];
    [twitterIDsNotUsingStamped_ removeObject:[friend objectForKey:@"id"]];
  }

  // Keep going since it chunks in 100-user bursts.
  [self requestTwitterUsersNotUsingStamped];
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK) {
    if (isSigningInToTwitter_)
      [self signOutOfTwitter:YES];
    if (isSigningInToFacebook_)
      [self signOutOfFacebook:YES];

    return;
  }

  if (!request.resourcePath && [request.URL.path rangeOfString:kTwitterUserLookupPath].location != NSNotFound) {
    // Fucking hell what a mess.
    NSError* err = nil;
    id body = [response parsedBody:&err];
    if (err) {
      NSLog(@"Parse error for request %@ response %@: %@", request.resourcePath, response, err);
      return;
    }

    [self didReceiveTwitterFriendsNotUsingStamped:body];
    return;
  }
  
  if ([request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound) {
    isSigningInToTwitter_ = NO;
    [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterRemovePath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookRemovePath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kTwitterSignOutURI].location != NSNotFound) {
    return;
  }

  NSError* err = nil;
  id body = [response parsedBody:&err];
  if (err) {
    NSLog(@"Parse error for request %@ response %@: %@", request.resourcePath, response, err);
    return;
  }

  // Response for requestTwitterUser.
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound) {
    [self requestStampedLinkTwitter:[body objectForKey:@"screen_name"]
                             userID:[body objectForKey:@"id_str"]
                              token:self.authentication.token
                             secret:self.authentication.tokenSecret];
    [self requestTwitterFriends:[body objectForKey:@"id_str"]];
  } else if ([request.resourcePath rangeOfString:kTwitterFriendsURI].location != NSNotFound) {
    self.twitterIDsNotUsingStamped = [NSMutableSet setWithArray:[body objectForKey:@"ids"]];
    [self requestStampedFriendsFromTwitter];
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  if (isSigningInToTwitter_)
    [self signOutOfTwitter:YES];
  if (isSigningInToFacebook_)
    [self signOutOfFacebook:YES];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

- (void)requestDidTimeout:(RKRequest*)request {
  if (isSigningInToTwitter_)
    [self signOutOfTwitter:YES];
  if (isSigningInToFacebook_)
    [self signOutOfFacebook:YES];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

- (void)requestDidCancelLoad:(RKRequest*)request {
  if (isSigningInToTwitter_)
    [self signOutOfTwitter:YES];
  if (isSigningInToFacebook_)
    [self signOutOfFacebook:YES];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSSortDescriptor* sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                                   ascending:YES 
                                                                    selector:@selector(localizedCaseInsensitiveCompare:)];

  if ([objectLoader.resourcePath rangeOfString:kStampedFindTwitterFriendsPath].location != NSNotFound) {
    NSArray* twitterFriends = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
    NSArray* friendIDs = [twitterFriends valueForKeyPath:@"identifier"];
    for (NSString* friendID in friendIDs) {
      NSNumber* n = [NSNumber numberWithInteger:friendID.integerValue];
      [twitterIDsNotUsingStamped_ removeObject:n];
    }

    [self requestTwitterUsersNotUsingStamped];
    [[NSNotificationCenter defaultCenter] postNotificationName:kTwitterFriendsChangedNotification object:twitterFriends];
  } else if ([objectLoader.resourcePath rangeOfString:kStampedFindFacebookFriendsPath].location != NSNotFound) {
    isSigningInToFacebook_ = NO;
    [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
    NSArray* facebookFriends = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
    NSArray* friendIDs = [facebookFriends valueForKeyPath:@"identifier"];
    NSMutableSet* friendSet = [NSMutableSet set];
    for (NSString* friendID in friendIDs)
      for (FacebookUser* user in facebookFriendsNotUsingStamped_)
        if ([user.facebookID isEqualToString:friendID])
          [friendSet addObject:user];

    for (FacebookUser* user in friendSet)
      [facebookFriendsNotUsingStamped_ removeObject:user];

    [[NSNotificationCenter defaultCenter] postNotificationName:kFacebookFriendsChangedNotification object:facebookFriends];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  if ([objectLoader.resourcePath rangeOfString:kStampedFindTwitterFriendsPath].location != NSNotFound) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kTwitterFriendsChangedNotification object:nil];
    self.twitterIDsNotUsingStamped = nil;
  }
  if ([objectLoader.resourcePath rangeOfString:kStampedFindFacebookFriendsPath].location != NSNotFound)
    [[NSNotificationCenter defaultCenter] postNotificationName:kFacebookFriendsChangedNotification object:nil];
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}


#pragma mark - Actions.

// This gets called when the app comes to the foreground, taking care of the case wherein
// the user returns from facebook and hasn't completed – or cancelled – the login process.
- (void)checkForEndlessSignIn:(NSNotification*)note {
  [[NSNotificationCenter defaultCenter] postNotificationName:kSocialNetworksChangedNotification object:self];
}

@end
