//
//  SharingSettingsViewController.m
//  Stamped
//
//  Created by Jake Zien on 10/31/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "SharingSettingsViewController.h"
#import "StampedAppDelegate.h"
#import "GTMOAuthAuthentication.h"
#import "Util.h"
#import "STOAuthViewController.h"

@interface SharingSettingsViewController ()

@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;
@property (nonatomic, retain) Facebook* fbClient;


-(void)updateUI;
-(void)signInToFacebook;
-(void)signOutOfFacebook;
-(GTMOAuthAuthentication*)createAuthentication;
-(void)signInToTwitter;
-(void)signOutOfTwitter;
-(void)fetchCurrentUser;
//-(void)setButton:(UIButton *)button connected:(BOOL)connected;

-(void)removeFBCredentials;
-(void)connectFacebookName:(NSString*)name userID:(NSString*)userID;
-(void)fetchFollowerIDs:(NSString*)userIDString;
-(void)connectTwitterUserName:(NSString*)username userID:(NSString*)userID;
-(void)connectTwitterFollowers:(NSArray*)followers;
-(void)connectFacebookFriends:(NSArray*)friends;

@end

static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kTwitterFollowersURI = @"/followers/ids.json";
static NSString* const kTwitterSignOutURI = @"/account/end_session.json";
static NSString* const kFacebookPermissionsURI = @"/me/permissions";
static NSString* const kFacebookFriendsURI = @"/me/friends";
static NSString* const kStampedTwitterLinkPath = @"/account/linked/twitter/update.json";
static NSString* const kStampedTwitterRemovePath = @"/account/linked/twitter/remove.json";
static NSString* const kStampedTwitterFollowersPath = @"/account/linked/twitter/followers.json";
static NSString* const kStampedFacebookLinkPath = @"/account/linked/facebook/update.json";
static NSString* const kStampedFacebookRemovePath = @"/account/linked/facebook/remove.json";
static NSString* const kStampedFacebookFriendsPath = @"/account/linked/facebook/followers.json";

@implementation SharingSettingsViewController

@synthesize twitterIconView;
@synthesize fbIconView;
@synthesize twitterConnectButton;
@synthesize fbConnectButton;
@synthesize twitterLabel;
@synthesize fbLabel;
@synthesize twitterNameLabel;
@synthesize fbNameLabel;
@synthesize scrollView;

@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;
@synthesize fbClient = fbClient_;

#pragma mark - View lifecycle

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [twitterClient_.requestQueue cancelRequestsWithDelegate:self];
  if ([fbClient_.sessionDelegate isEqual:self])
    fbClient_.sessionDelegate = nil;
  self.twitterIconView = nil;
  self.fbIconView = nil;
  self.twitterConnectButton = nil;
  self.fbConnectButton = nil;
  self.twitterLabel = nil;
  self.fbLabel = nil;
  self.twitterNameLabel = nil;
  self.fbNameLabel = nil;
  self.authentication = nil;
  self.twitterClient = nil;
  self.fbClient = nil;
  self.scrollView = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  self.navigationItem.title = @"Sharing";
  self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  self.scrollView.contentSize = CGSizeMake(self.scrollView.bounds.size.width, self.scrollView.bounds.size.height + 1);
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [twitterClient_.requestQueue cancelRequestsWithDelegate:self];
  if ([fbClient_.sessionDelegate isEqual:self])
    fbClient_.sessionDelegate = nil;
  self.twitterIconView = nil;
  self.fbIconView = nil;
  self.twitterConnectButton = nil;
  self.fbConnectButton = nil;
  self.twitterLabel = nil;
  self.fbLabel = nil;
  self.twitterNameLabel = nil;
  self.fbNameLabel = nil;
  self.authentication = nil;
  self.twitterClient = nil;
  self.fbClient = nil;
  self.scrollView = nil;
  [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
  self.navigationController.navigationBarHidden = YES;
  [self updateUI];
  [super viewWillAppear:animated];
}

#pragma mark - Actions

- (IBAction)twitterButtonPressed:(id)sender {
  GTMOAuthAuthentication* auth = [self createAuthentication];
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    [self signOutOfTwitter];
  } 
  else {
    [self signInToTwitter];
  }
  [self updateUI];
}

- (IBAction)fbButtonPressed:(id)sender {
  if (!self.fbClient.isSessionValid)
    [self signInToFacebook];
  else
    [self signOutOfFacebook];
  [self updateUI];
}

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

#pragma mark - Private

- (void)updateUI {
  // Check for a valid Twitter session before updating.
  GTMOAuthAuthentication* auth = [self createAuthentication];
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    self.authentication = auth;
    CGRect frame = self.twitterConnectButton.frame;
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      self.twitterConnectButton.selected = YES;
      self.twitterConnectButton.frame = CGRectMake(210, frame.origin.y, 90, frame.size.height);
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_on"];
      NSString* name = [[NSUserDefaults standardUserDefaults] objectForKey:@"TwitterUsername"];
      if (name) {
        self.twitterLabel.frame = CGRectMake(53, 29, 138, 21);
        if (![self.twitterNameLabel.text isEqualToString:name])
          self.twitterNameLabel.text = name;
        self.twitterNameLabel.alpha = 1.0;
      }
    }
    completion:nil];
  } 
  else {
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.twitterConnectButton.frame;
      self.twitterConnectButton.selected = NO;
      self.twitterLabel.frame = CGRectMake(53, 37, 138, 21);
      self.twitterNameLabel.alpha = 0.0;
      self.twitterConnectButton.frame = CGRectMake(225, frame.origin.y, 75, frame.size.height);
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_off"];
    }
    completion:nil];
  }

  // Check for a valid FB session before updating.
  if (!self.fbClient)
    self.fbClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.fbClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.fbClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  
  if (self.fbClient.isSessionValid) {
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.fbConnectButton.frame;
      self.fbConnectButton.selected = YES;
      self.fbConnectButton.frame = CGRectMake(210, frame.origin.y, 90, frame.size.height);
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_on"];
      NSString* name = [[NSUserDefaults standardUserDefaults] objectForKey:@"FBName"];
      if (name) {
        self.fbLabel.frame = CGRectMake(53, 102, 138, 21);
        if (![self.fbNameLabel.text isEqualToString:name])
          self.fbNameLabel.text = name;
        self.fbNameLabel.alpha = 1.0;
      }
    }
    completion:nil];
  }
  else {    
    [UIView animateWithDuration:0.25 delay:0 options:UIViewAnimationCurveEaseIn animations:^{
      CGRect frame = self.fbConnectButton.frame;
      self.fbConnectButton.selected = NO;
      self.fbConnectButton.frame = CGRectMake(225, frame.origin.y, 75, frame.size.height);
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_off"];
      self.fbLabel.frame = CGRectMake(53, 110, 138, 21);
      self.fbNameLabel.alpha = 0.0;
    }
    completion:nil];
  }
  
}

#pragma mark - Facebook

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

- (void)fbDidLogin {
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:[self.fbClient accessToken] forKey:@"FBAccessTokenKey"];
  [defaults setObject:[self.fbClient expirationDate] forKey:@"FBExpirationDateKey"];
  [defaults synchronize];
  [self.fbClient requestWithGraphPath:@"me" andDelegate:self];
}

- (void)fbDidNotLogin:(BOOL)cancelled {
  NSLog(@"whoa, no fb login");
  [self removeFBCredentials];
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

- (void)signInToTwitter {
  GTMOAuthAuthentication *auth = [self createAuthentication];
  if (auth == nil) {
    NSAssert(NO, @"A valid consumer key and consumer secret are required for signing in to Twitter");
  }
  
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
  
  [self.navigationController pushViewController:authVC animated:YES];
  [authVC release];
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

- (void)fetchCurrentUser {
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:self];
  request.cachePolicy = RKRequestCachePolicyNone;
  [request prepareURLRequest];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)fetchFollowerIDs:(NSString*)userIDString {
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
    // TODO: sign out of twitter
    [self updateUI];
    return;
  }
  self.authentication = auth;
  [self fetchCurrentUser];  
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
  [self updateUI];
  if (!response.isOK) {
    if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound && 
        response.statusCode == 401)
      [self signOutOfTwitter];
    NSLog(@"HTTP error for request: %@, response: %d", request.resourcePath, response.statusCode);
    [self updateUI];
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound) {
    NSLog(@"Linked Twitter successfully.");
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterRemovePath].location != NSNotFound) {
    NSLog(@"Unlinked Twitter successfully.");
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound) {
    NSLog(@"Linked Twitter followers successfully.");
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound) {
    NSLog(@"Linked Facebook successfully.");
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookRemovePath].location != NSNotFound) {
    NSLog(@"Unlinked Facebook successfully.");
    return;
  }
  if ([request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound) {
    NSLog(@"Linked Facebook friends successfully.");
    return;
  }
  if ([request.resourcePath isEqualToString:kTwitterSignOutURI]) {
    NSLog(@"Signed out of Twitter.");
    [self updateUI];
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
    [self fetchFollowerIDs:[body objectForKey:@"id_str"]];
  }
  // Response for getting Twitter followers. 
  else if ([request.resourcePath rangeOfString:kTwitterFollowersURI].location != NSNotFound) {
    [self connectTwitterFollowers:[body objectForKey:@"ids"]];
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  NSLog(@"Error %@ for request %@", error, request.resourcePath);
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterLinkPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kStampedTwitterFollowersPath].location != NSNotFound)
    [self signOutOfTwitter];
  else if ([request.resourcePath rangeOfString:kStampedFacebookLinkPath].location != NSNotFound ||
           [request.resourcePath rangeOfString:kStampedFacebookFriendsPath].location != NSNotFound)
    [self signOutOfFacebook];
  [self updateUI];
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

/*
- (void)setButton:(UIButton *)button connected:(BOOL)connected {
  UIImage* connectImg = [UIImage imageNamed:@"settings_sharing_button_connect"];
  UIImage* disconnectImg = [UIImage imageNamed:@"settings_sharing_button_disconnect"];
  
  if (connected) {
    button.imageView.image = disconnectImg;
    CGRect frame = button.frame;
    frame.size.width = disconnectImg.size.width;
    frame.origin.x -= disconnectImg.size.width - connectImg.size.width;
    button.frame = frame;
    if ([button isEqual:self.twitterConnectButton])
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_on"];
    else if ([button isEqual:self.fbConnectButton])
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_on"];                                    
  }
  else {
    button.imageView.image = connectImg;
    CGRect frame = button.frame;
    frame.size.width = connectImg.size.width;
    frame.origin.x += disconnectImg.size.width - connectImg.size.width;
    button.frame = frame;
    if ([button isEqual:self.twitterConnectButton])
      self.twitterIconView.image = [UIImage imageNamed:@"settings_sharing_twitter_off"];
    else if ([button isEqual:self.fbConnectButton])
      self.fbIconView.image = [UIImage imageNamed:@"settings_sharing_facebook_off"];
  }
}
*/

@end
