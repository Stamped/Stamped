//
//  SharedRequestDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "SharedRequestDelegate.h"

#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Comment.h"
#import "Stamp.h"
#import "Util.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"
#import "GTMOAuthAuthentication.h"
#import "STOAuthViewController.h"

static SharedRequestDelegate* sharedDelegate_ = nil;

static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kTwitterFollowersURI = @"/followers/ids.json";
static NSString* const kTwitterSignOutURI = @"/account/end_session.json";
//static NSString* const kFacebookPermissionsURI = @"/me/permissions";
static NSString* const kFacebookFriendsURI = @"/me/friends";
static NSString* const kStampedTwitterLinkPath = @"/account/linked/twitter/update.json";
static NSString* const kStampedTwitterRemovePath = @"/account/linked/twitter/remove.json";
static NSString* const kStampedTwitterFollowersPath = @"/account/linked/twitter/followers.json";
static NSString* const kStampedFacebookLinkPath = @"/account/linked/facebook/update.json";
static NSString* const kStampedFacebookRemovePath = @"/account/linked/facebook/remove.json";
static NSString* const kStampedFacebookFriendsPath = @"/account/linked/facebook/followers.json";

@interface SharedRequestDelegate ()

- (void)signInToFacebook;
- (void)signOutOfFacebook;
- (void)removeFBCredentials;
- (void)connectFacebookName:(NSString*)name userID:(NSString*)userID;
- (void)connectFacebookFriends:(NSArray*)friends;
- (GTMOAuthAuthentication*)createAuthentication;
- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error;  
- (void)signOutOfTwitter;
- (void)fetchCurrentUserFromTwitter;
- (void)fetchFollowerIDsFromTwitterForUser:(NSString*)userIDString;
- (void)connectTwitterUserName:(NSString*)username userID:(NSString*)userID;
- (void)connectTwitterFollowers:(NSArray*)followers;

@property (nonatomic, retain) Facebook* fbClient;
@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;

@end


@implementation SharedRequestDelegate

@synthesize fbClient = fbClient_;
@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;

+ (SharedRequestDelegate*)sharedDelegate {
  if (sharedDelegate_ == nil)
    sharedDelegate_ = [[super allocWithZone:NULL] init];
  
  return sharedDelegate_;
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedDelegate] retain];
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

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	if ([objectLoader.resourcePath isEqualToString:kRemoveCommentPath]) {
    Comment* comment = [objects lastObject];
    [Comment.managedObjectContext deleteObject:comment];
    [Comment.managedObjectContext save:NULL];
  } if ([objectLoader.resourcePath isEqualToString:kRemoveStampPath]) {
    Stamp* stamp = [objects lastObject];
    [Stamp.managedObjectContext deleteObject:stamp];
    [Stamp.managedObjectContext save:NULL];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];
}

#pragma mark - Facebook

- (void)fbDidLogin {  
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:[self.fbClient accessToken] forKey:@"FBAccessTokenKey"];
  [defaults setObject:[self.fbClient expirationDate] forKey:@"FBExpirationDateKey"];
  [defaults synchronize];
  [self.fbClient requestWithGraphPath:@"me" andDelegate:self];
}

- (void)fbDidNotLogin:(BOOL)cancelled {
  [self signOutOfFacebook];
}

- (void)signInToFacebook {
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.fbClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.fbClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  if (!self.fbClient.isSessionValid) {
    self.fbClient.sessionDelegate = self;
    [self.fbClient authorize:[[NSArray alloc] initWithObjects:@"offline_access", @"publish_stream", nil]];
  }
}

- (void)signOutOfFacebook {
  [self.fbClient logout:self];
  [self removeFBCredentials];
  // Unlink the Facebook info from the user's account on the backend.
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedFacebookRemovePath delegate:self];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)removeFBCredentials {
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"]) {
    [defaults removeObjectForKey:@"FBAccessTokenKey"];
    [defaults removeObjectForKey:@"FBExpirationDateKey"];
    [defaults removeObjectForKey:@"FBName"];
    [defaults removeObjectForKey:@"FBID"];
    [defaults synchronize];
    
    // Nil out the session variables to prevent
    // the app from thinking there is a valid session
    if (nil != self.fbClient.accessToken) {
      self.fbClient.accessToken = nil;
    }
    if (nil != self.fbClient.expirationDate) {
      self.fbClient.expirationDate = nil;
    }
  }
}

- (void)connectFacebookName:(NSString*)name userID:(NSString*)userID {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:name forKey:@"FBName"];
  [defaults setObject:userID forKey:@"FBID"];
  [defaults synchronize];
  
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedFacebookLinkPath
                                                               delegate:self];
  
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"facebook_id", name, @"facebook_name", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)connectFacebookFriends:(NSArray*)friends {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedFacebookFriendsPath delegate:self];
  request.params = [NSDictionary dictionaryWithObject:[friends componentsJoinedByString:@","] forKey:@"q"];
  request.method = RKRequestMethodPOST;
  [request send];
}

#pragma mark - FBRequestDelegate Methods.

- (void)request:(FBRequest*)request didLoad:(id)result {
  NSArray* resultData;
  
  if ([result isKindOfClass:[NSArray class]])
    result = [result objectAtIndex:0];
  if ([result isKindOfClass:[NSDictionary class]]) {
    // handle callback from request for current user info.
    if ([result objectForKey:@"name"]) {
      [self connectFacebookName:[result objectForKey:@"name"] userID:[result objectForKey:@"id"]];
      [self.fbClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
    }
    resultData = [result objectForKey:@"data"];
  }
  
  // handle callback from request for user's friends.
  if (resultData  &&  resultData.count != 0) {
    NSMutableArray* fbFriendIDs = [NSMutableArray array];
    for (NSDictionary* dict in resultData)
      [fbFriendIDs addObject:[dict objectForKey:@"id"]];
    if (fbFriendIDs.count > 0) {
      [self connectFacebookFriends:fbFriendIDs];
    }
  }
}

- (void)request:(FBRequest*)request didFailWithError:(NSError *)error {
  NSLog(@"FB err code: %d", [error code]);
  NSLog(@"FB err message: %@", [error description]);
  if (error.code == 10000)
    [self signOutOfFacebook];
}


#pragma mark - Twitter

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

- (void)signOutOfTwitter {
  [GTMOAuthViewControllerTouch removeParamsFromKeychainForName:kKeychainTwitterToken];
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterSignOutURI delegate:self];
  request.method = RKRequestMethodPOST;
  [request prepareURLRequest];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
  // Unlink the Twitter info from the user's account on the backend.
  RKRequest* unlinkRequest = [[RKClient sharedClient] requestWithResourcePath:kStampedTwitterRemovePath delegate:self];
  unlinkRequest.method = RKRequestMethodPOST;
  [unlinkRequest send];
  [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"TwitterUsername"];
  [[NSUserDefaults standardUserDefaults] synchronize]; 
}

- (void)fetchCurrentUserFromTwitter {
  if (!self.twitterClient)
    self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:self];
  request.cachePolicy = RKRequestCachePolicyNone;
  [request prepareURLRequest];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)fetchFollowerIDsFromTwitterForUser:(NSString*)userIDString {
  if (!self.twitterClient)
    self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  NSString* path =
  [kTwitterFollowersURI appendQueryParams:[NSDictionary dictionaryWithObjectsAndKeys:@"-1", @"cursor", userIDString, @"user_id", nil]];
  RKRequest* request = [self.twitterClient requestWithResourcePath:path delegate:self];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error {  
  if (error) {
    NSLog(@"GTMOAuth error = %@", error);
    [self signOutOfTwitter];
    return;
  }
  self.authentication = auth;
  if (!self.twitterClient)
    self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  [self fetchCurrentUserFromTwitter];  
}

- (void)connectTwitterUserName:(NSString*)username userID:(NSString*)userID {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:username forKey:@"TwitterUsername"];
  [defaults synchronize];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedTwitterLinkPath
                                                               delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"twitter_id",
                    username, @"twitter_screen_name", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}

- (void)connectTwitterFollowers:(NSArray*)followers {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedTwitterFollowersPath delegate:self];
  request.params = [NSDictionary dictionaryWithObject:[followers componentsJoinedByString:@","] forKey:@"q"];
  request.method = RKRequestMethodPOST;
  [request send];
}

#pragma mark - RKRequestDelegate Methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK) {
    if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound && 
        response.statusCode == 401)
      [self signOutOfTwitter];
    NSLog(@"HTTP error for request: %@, response: %d", request.resourcePath, response.statusCode);
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterRemovePath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookRemovePath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound) {
    return;
  }
  if ([request.resourcePath isEqualToString:kTwitterSignOutURI]) {
    return;
  }
  
  NSError* err = nil;
  id body = [response parsedBody:&err];
  if (err) {
    NSLog(@"Parse error for request %@ response %@: %@", request.resourcePath, response, err);
    return;
  }
  
  // Response for getting the current user information.
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound) {
    [self connectTwitterUserName:[body objectForKey:@"screen_name"] userID:[body objectForKey:@"id_str"]];
    [self fetchFollowerIDsFromTwitterForUser:[body objectForKey:@"id_str"]];
  }
  // Response for getting Twitter followers. 
  else if ([request.resourcePath rangeOfString:kTwitterFollowersURI].location != NSNotFound) {
    [self connectTwitterFollowers:[body objectForKey:@"ids"]];
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound)
    [self signOutOfTwitter];
  else if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound ||
           [request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound)
    [self signOutOfFacebook];
}

- (void)requestDidTimeout:(RKRequest *)request {
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound)
    [self signOutOfTwitter];
  else if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound ||
           [request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound)
    [self signOutOfFacebook];
}

- (void)requestDidCancelLoad:(RKRequest *)request {
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound)
    [self signOutOfTwitter];
  else if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound ||
           [request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound)
    [self signOutOfFacebook];
}

@end
