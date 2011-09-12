//
//  FindFriendsViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "FindFriendsViewController.h"

#import "GTMOAuthAuthentication.h"
#import "GTMOAuthViewControllerTouch.h"

#import "STSectionHeaderView.h"
#import "Util.h"

// Constants ///////////////////////////////////////////////////////////////////

NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
NSString* const kTwitterFriendsURI = @"/friends/ids.json";
NSString* const kStampedTwitterFriendsURI = @"/users/find/twitter.json";

// Private Interface ///////////////////////////////////////////////////////////

@interface FindFriendsViewController ()

@property (nonatomic, assign) FindFriendsSource findSource;
@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;

- (void)adjustNippleToView:(UIView*)view;
- (GTMOAuthAuthentication*)createAuthentication;
- (void)signInToTwitter;
- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error;

- (void)fetchCurrentUser;
- (void)fetchFriendIDs:(NSString*)userIDString;
- (void)findStampedFriendsFromTwitter:(NSArray*)twitterIDs;
@end

// Implementation //////////////////////////////////////////////////////////////

@implementation FindFriendsViewController

@synthesize findSource = findSource_;
@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;

@synthesize contactsButton = contactsButton_;
@synthesize twitterButton = twitterButton_;
@synthesize nipple = nipple_;

- (id)initWithFindSource:(FindFriendsSource)source {
  if ((self = [self initWithNibName:@"FindFriendsView" bundle:nil])) {
    self.findSource = source;
  }
  return self;
}

- (void)dealloc {
  self.authentication = nil;
  [super dealloc];
}

#pragma mark - View Lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
}

- (void)viewDidUnload {
  self.twitterClient = nil;

  [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
  if (self.findSource == FindFriendsFromContacts)
    [self findFromContacts:self];
  else if (self.findSource == FindFriendsFromTwitter)
    [self findFromTwitter:self];
  //else
  //  NSAssert(NO, @"Find source %d invalid", self.findSource);  // Causing an error on archive build!?
}

#pragma mark - Actions

- (IBAction)done:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)findFromContacts:(id)sender {
  [self.contactsButton setImage:[UIImage imageNamed:@"contacts_icon"]
                       forState:UIControlStateNormal];
  [self.twitterButton setImage:[UIImage imageNamed:@"twitter_icon_disabled"]
                      forState:UIControlStateNormal];
  [self adjustNippleToView:self.contactsButton];
}

- (IBAction)findFromTwitter:(id)sender {
  [self.contactsButton setImage:[UIImage imageNamed:@"contacts_icon_disabled"]
                       forState:UIControlStateNormal];
  [self.twitterButton setImage:[UIImage imageNamed:@"twitter_logo"]
                      forState:UIControlStateNormal];
  [self adjustNippleToView:self.twitterButton];

  GTMOAuthAuthentication* auth = [self createAuthentication];
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    self.authentication = auth;
    [self fetchCurrentUser];
    // TODO: kick off friend request
  } else {
    [self signInToTwitter];
  }
}

#pragma mark - Table View Delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];
  view.leftLabel.text = @"Contacts using Stamped";
  view.rightLabel.text = @"42";
  return view;
}

#pragma mark - Private

// Takes in a view and centers the |nipple_|'s X position to be the midpoint of
// |view|'s frame. This does not adjust the Y position of the nipple.
- (void)adjustNippleToView:(UIView*)view {
  CGRect nippleFrame = self.nipple.frame;

  const CGFloat targetMidX = CGRectGetMidX([view frame]);
  const CGFloat nippleMidX = CGRectGetMidX(nippleFrame);
  const CGFloat nippleMinX = CGRectGetMinX(nippleFrame);

  nippleFrame.origin.x = targetMidX - (nippleMidX - nippleMinX);

  [UIView animateWithDuration:0.1 animations:^(void) {
    self.nipple.frame = nippleFrame;
  }];
}

- (GTMOAuthAuthentication*)createAuthentication {
  GTMOAuthAuthentication* auth =
      [[GTMOAuthAuthentication alloc] initWithSignatureMethod:kGTMOAuthSignatureMethodHMAC_SHA1
                                                  consumerKey:kTwitterConsumerKey
                                                   privateKey:kTwitterConsumerSecret];
  auth.callback = kOAuthCallbackURL;
  return [auth autorelease];
}

- (void)signInToTwitter {
  GTMOAuthViewControllerTouch* authVC =
      [[GTMOAuthViewControllerTouch alloc] initWithScope:kTwitterScope
                                                language:nil
                                         requestTokenURL:[NSURL URLWithString:kTwitterRequestTokenURL]
                                       authorizeTokenURL:[NSURL URLWithString:kTwitterAuthorizeURL]
                                          accessTokenURL:[NSURL URLWithString:kTwitterAccessTokenURL]
                                          authentication:[self createAuthentication]
                                          appServiceName:kKeychainTwitterToken
                                                delegate:self
                                        finishedSelector:@selector(viewController:finishedWithAuth:error:)];
  [self.navigationController pushViewController:authVC animated:YES];
  [authVC release];
}

- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error {
  if (error) {
    NSLog(@"GTMOAuth error = %@", error);
    return;
  }
  //NSAssert(!error, @"GTMOAuth error = %@", error);  // TODO: probably do something less bad.
  self.authentication = auth;
}

#pragma mark - Twitter

- (void)fetchCurrentUser {
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:self];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)fetchFriendIDs:(NSString*)userIDString {
  NSString* path = [NSString stringWithFormat:@"%@?cursor=-1&user_id=%@", kTwitterFriendsURI, userIDString];
  RKRequest* request = [self.twitterClient requestWithResourcePath:path delegate:self];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)findStampedFriendsFromTwitter:(NSArray*)twitterIDs {
  // TODO: the server only supports 100 IDs at a time. need to chunk.
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];

  NSString* path = [NSString stringWithFormat:@"%@?q=%@",
      kStampedTwitterFriendsURI, [twitterIDs componentsJoinedByString:@","]];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:path
                                                        delegate:self];
  loader.objectMapping = mapping;
  [loader send];
}

#pragma mark - RestKit Delegate

// Requests ////////////////////////////////////////////////////////////////////

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK) {
    NSLog(@"HTTP error for request: %@, response: %@", request, response);
    return;
  }

  NSError* err = nil;
  id body = [response parsedBody:&err];
  if (err) {
    NSLog(@"Parse error for response %@: %@", response, err);
    return;
  }

  // Response for getting the current user information.
  if ([request.resourcePath rangeOfString:kTwitterCurrentUserURI].location != NSNotFound) {
    // TODO: send to Stamped server the username.
    // Fetch the list of all the users this user is following.
    [self fetchFriendIDs:[body objectForKey:@"id_str"]];
  }

  // Response for getting Twitter friends. Send on to Stamped to find any
  // Stamped friends.
  else if ([request.resourcePath rangeOfString:kTwitterFriendsURI].location != NSNotFound) {
    [self findStampedFriendsFromTwitter:[body objectForKey:@"ids"]];
  }

  // Catch-all.
  else {
    NSLog(@"Received respose %@ for unknown request %@", response, request);
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  NSLog(@"Twitter error %@ for request %@", error, request);
}

// Object Loader ///////////////////////////////////////////////////////////////

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSLog(@"got users: %@", objects);
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"Object loader %@ did fail with error %@", objectLoader, error);
}

@end
