//
//  FindFriendsViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "FindFriendsViewController.h"

#import <AddressBook/AddressBook.h>
#import <RestKit/CoreData/CoreData.h>

#import "GTMOAuthAuthentication.h"
#import "GTMOAuthViewControllerTouch.h"

#import "FBConnect.h"
#import "Facebook.h"

#import "STSectionHeaderView.h"
#import "STSearchField.h"
#import "StampedAppDelegate.h"
#import "FriendshipTableViewCell.h"
#import "Stamp.h"
#import "Util.h"
#import "User.h"

static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kFacebookFriendsURI = @"/me/friends";
static NSString* const kStampedTwitterFriendsURI = @"/users/find/twitter.json";
static NSString* const kStampedFacebookFriendsURI = @"/users/find/facebook.json";
static NSString* const kStampedEmailFriendsURI = @"/users/find/email.json";
static NSString* const kStampedPhoneFriendsURI = @"/users/find/phone.json";
static NSString* const kStampedSearchURI = @"/users/search.json";
static NSString* const kStampedLinkedAccountsURI = @"/account/linked_accounts.json";
static NSString* const kFriendshipCreatePath = @"/friendships/create.json";
static NSString* const kFriendshipRemovePath = @"/friendships/remove.json";
//static NSString* const kFacebookAppID = @"297022226980395";

@interface FindFriendsViewController ()
- (void)adjustNippleToView:(UIView*)view;
- (void)setSearchFieldHidden:(BOOL)hidden animated:(BOOL)animated;
- (GTMOAuthAuthentication*)createAuthentication;
- (void)signInToTwitter;
- (void)sendRelationshipChangeRequestWithPath:(NSString*)path forUser:(User*)user;
- (void)followButtonPressed:(id)sender;
- (void)unfollowButtonPressed:(id)sender;
- (FriendshipTableViewCell*)friendshipCellFromSubview:(UIView*)view;
- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error;
- (void)connectTwitterUserName:(NSString*)username userID:(NSString*)userID;
- (void)connectFacebookName:(NSString*)name userID:(NSString*)userID;
- (void)fetchCurrentUser;
- (void)fetchFriendIDs:(NSString*)userIDString;
- (void)findStampedFriendsFromTwitter:(NSArray*)twitterIDs;
- (void)findStampedFriendsFromFacebook:(NSArray*)facebookIDs;
- (void)findStampedFriendsFromEmails:(NSArray*)emails andNumbers:(NSArray*)numbers;
- (void)signInToFacebook;
- (void)checkForEndlessSignIn;
//- (void)loadSignInView;

@property (nonatomic, assign) FindFriendsSource findSource;
@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;
@property (nonatomic, retain) Facebook* facebookClient;
@property (nonatomic, copy) NSArray* twitterFriends;
@property (nonatomic, copy) NSArray* contactFriends;
@property (nonatomic, copy) NSArray* stampedFriends;
@property (nonatomic, copy) NSArray* facebookFriends;
@property (nonatomic, assign) BOOL searchFieldHidden;
@property (nonatomic, assign) BOOL twitterAuthFailed;
@end

@implementation FindFriendsViewController

@synthesize findSource = findSource_;
@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;
@synthesize twitterFriends = twitterFriends_;
@synthesize facebookClient = facebookClient_;
@synthesize contactFriends = contactFriends_;
@synthesize stampedFriends = stampedFriends_;
@synthesize facebookFriends = facebookFriends_;
@synthesize followedUsers = followedUsers_;
@synthesize contactsButton = contactsButton_;
@synthesize twitterButton = twitterButton_;
@synthesize facebookButton = facebookButton_;
@synthesize stampedButton = stampedButton_;
@synthesize searchField = searchField_;
@synthesize nipple = nipple_;
@synthesize tableView = tableView_;
@synthesize searchFieldHidden = searchFieldHidden_;
@synthesize twitterAuthFailed = twitterAuthFailed_;
@synthesize signInTwitterView = signInTwitterView_;
@synthesize signInFacebookView = signInFacebookView_;
@synthesize signInAuthView = signInAuthView_;
@synthesize signInTwitterActivityIndicator = signInTwitterActivityIndicator_;
@synthesize signInFacebookActivityIndicator = signInFacebookActivityIndicator_;
@synthesize signInTwitterConnectButton = signinTwitterConnectButton_;
@synthesize signInFacebookConnectButton = signInFacebookConnectButton_;

- (id)initWithFindSource:(FindFriendsSource)source {
  if ((self = [self initWithNibName:@"FindFriendsView" bundle:nil])) {
    self.findSource = source;
    self.followedUsers = [NSMutableArray array];
  }
  return self;
}


- (void)dealloc {
  self.followedUsers = nil;
  self.authentication = nil;
  self.twitterClient = nil;
  self.twitterFriends = nil;
  self.contactFriends = nil;
  self.contactsButton = nil;
  self.twitterButton = nil;
  self.facebookButton = nil;
  self.stampedButton = nil;
  self.searchField = nil;
  self.facebookClient = nil;
  self.nipple = nil;
  self.tableView = nil;
  self.signInTwitterView = nil;
  self.signInFacebookView = nil;
  self.signInAuthView = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
  self.signInTwitterConnectButton = nil;
  self.signInFacebookConnectButton = nil;
  
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  
  [super dealloc];
}

#pragma mark - View Lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  searchFieldHidden_ = YES;
  self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  self.facebookClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(checkForEndlessSignIn)
                                               name:UIApplicationDidBecomeActiveNotification
                                             object:nil];
    
  if (self.findSource == FindFriendsFromStamped)
    [self findFromStamped:self];
  else if (self.findSource == FindFriendsFromContacts)
    [self findFromContacts:self];
  else if (self.findSource == FindFriendsFromTwitter)
    [self findFromTwitter:self];
  else if (self.findSource == FindFriendsFromFacebook)
    [self findFromFacebook:self];
  else
    [self findFromStamped:self];
}

- (void)viewDidUnload {
  self.twitterClient = nil;
  self.twitterFriends = nil;
  self.contactFriends = nil;
  self.contactsButton = nil;
  self.twitterButton = nil;
  self.facebookButton = nil;
  self.stampedButton = nil;
  self.nipple = nil;
  self.searchField = nil;
  self.facebookClient = nil;
  self.tableView = nil;
  self.signInTwitterView = nil;
  self.signInFacebookView = nil;
  self.signInAuthView = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
  self.signInTwitterConnectButton = nil;
  self.signInFacebookConnectButton = nil;

  [[NSNotificationCenter defaultCenter] removeObserver:self];
  
  [super viewDidUnload];
}

#pragma mark - Actions

- (IBAction)done:(id)sender {
  UIViewController* vc = nil;
  if ([self respondsToSelector:@selector(presentingViewController)])
    vc = [(id)self presentingViewController];
  else
    vc = self.parentViewController;
  
  [vc dismissModalViewControllerAnimated:YES];
}

- (IBAction)findFromStamped:(id)sender {
  self.signInTwitterView.hidden = YES;
  self.signInFacebookView.hidden = YES;
  [self setSearchFieldHidden:NO animated:YES];
  tableView_.hidden = YES;
  self.stampedFriends = nil;
  [self.tableView reloadData];
  contactsButton_.selected = NO;
  twitterButton_.selected = NO;
  facebookButton_.selected = NO;
  stampedButton_.selected = YES;
  [searchField_ becomeFirstResponder];
  
  [self adjustNippleToView:self.stampedButton];
  self.findSource = FindFriendsFromStamped;
  [tableView_ reloadData];
}

- (IBAction)findFromContacts:(id)sender {
  [self setSearchFieldHidden:YES animated:NO];
  self.signInTwitterView.hidden = YES;
  self.signInFacebookView.hidden = YES;
  tableView_.hidden = NO;
  contactsButton_.selected = YES;
  twitterButton_.selected = NO;
  facebookButton_.selected = NO;
  stampedButton_.selected = NO;
  [searchField_ resignFirstResponder];
  [self adjustNippleToView:self.contactsButton];
  self.findSource = FindFriendsFromContacts;
  if (contactFriends_) {
    [self.tableView reloadData];
    return;
  }
  // Fetch the address book 
  ABAddressBookRef addressBook = ABAddressBookCreate();
  CFArrayRef people = ABAddressBookCopyArrayOfAllPeople(addressBook);
  CFIndex numPeople = ABAddressBookGetPersonCount(addressBook);
  NSMutableArray* allNumbers = [NSMutableArray array];
  NSMutableArray* allEmails = [NSMutableArray array];
  for (NSUInteger i = 0; i < numPeople; ++i) {
    ABRecordRef person = CFArrayGetValueAtIndex(people, i);
    ABMultiValueRef phoneNumberProperty = ABRecordCopyValue(person, kABPersonPhoneProperty);
    NSArray* phoneNumbers = (NSArray*)ABMultiValueCopyArrayOfAllValues(phoneNumberProperty);
    CFRelease(phoneNumberProperty);
    [allNumbers addObjectsFromArray:phoneNumbers];
    [phoneNumbers release];

    ABMultiValueRef emailProperty = ABRecordCopyValue(person, kABPersonEmailProperty);
    NSArray* emails = (NSArray*)ABMultiValueCopyArrayOfAllValues(emailProperty);
    CFRelease(emailProperty);
    [allEmails addObjectsFromArray:emails];
    [emails release];
  }
  CFRelease(addressBook);
  CFRelease(people);
  NSMutableArray* sanitizedNumbers = [NSMutableArray array];
  for (NSString* num in allNumbers) {
    NSString* sanitized = [Util sanitizedPhoneNumberFromString:num];
    if (sanitized)
      [sanitizedNumbers addObject:sanitized];
  }
  [self findStampedFriendsFromEmails:allEmails andNumbers:sanitizedNumbers];
  [tableView_ reloadData];
}

- (IBAction)findFromTwitter:(id)sender {
  [self setSearchFieldHidden:YES animated:NO];
  tableView_.hidden = NO;
  contactsButton_.selected = NO;
  twitterButton_.selected = YES;
  facebookButton_.selected = NO;
  stampedButton_.selected = NO;
  [searchField_ resignFirstResponder];
  [self adjustNippleToView:self.twitterButton];
  self.findSource = FindFriendsFromTwitter;

  if (twitterFriends_) {
    [self.tableView reloadData];
    return;
  }

  GTMOAuthAuthentication* auth = [self createAuthentication];
  if ([GTMOAuthViewControllerTouch authorizeFromKeychainForName:kKeychainTwitterToken
                                                 authentication:auth]) {
    self.authentication = auth;
    [self fetchCurrentUser];
  } else {
    self.tableView.hidden = YES;
    self.signInFacebookView.hidden = YES;
    self.signInTwitterView.hidden = NO;
  }
  [tableView_ reloadData];
}

- (IBAction)findFromFacebook:(id)sender {
  [self setSearchFieldHidden:YES animated:NO];
  tableView_.hidden = NO;
  contactsButton_.selected = NO;
  twitterButton_.selected = NO;
  facebookButton_.selected = YES;
  stampedButton_.selected = NO;
  [searchField_ resignFirstResponder];
  [self adjustNippleToView:facebookButton_];
  self.findSource = FindFriendsFromFacebook;
  
  if (facebookFriends_) {
    [self.facebookClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
    [self.tableView reloadData];
    return;
  }
  
  
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.facebookClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.facebookClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  
  if (!self.facebookClient.isSessionValid) {
    self.tableView.hidden = YES;
    self.signInFacebookView.hidden = NO;
    self.signInTwitterView.hidden = YES;
    return;
  }
  
  [self.facebookClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
  [tableView_ reloadData];
}

- (void)setSearchFieldHidden:(BOOL)hidden animated:(BOOL)animated {
  if (hidden == searchFieldHidden_)
    return;

  searchFieldHidden_ = hidden;

  CGFloat yOffset = -26;
  if (!hidden) {
    yOffset *= -1;
    searchField_.text = nil;
  }

  if (animated) {
  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     tableView_.frame = CGRectOffset(CGRectInset(tableView_.frame, 0, yOffset), 0, yOffset);
                   }
                   completion:^(BOOL finished){
                     searchField_.text = nil;
                   }];
  }
  else {
    tableView_.frame = CGRectOffset(CGRectInset(tableView_.frame, 0, yOffset), 0, yOffset);
    searchField_.text = nil;
  }
}

- (FriendshipTableViewCell*)friendshipCellFromSubview:(UIView*)view {
  UIView* superview = view.superview;
  while (superview && ![superview isMemberOfClass:[FriendshipTableViewCell class]]) {
    superview = superview.superview;
  }
  FriendshipTableViewCell* cell = (FriendshipTableViewCell*)superview;
  return cell;
}

- (void)sendRelationshipChangeRequestWithPath:(NSString*)path forUser:(User*)user {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:user.userID, @"user_id", nil];
  [objectLoader send];
}

- (void)followButtonPressed:(id)sender {
  FriendshipTableViewCell* cell = [self friendshipCellFromSubview:sender];
  [followedUsers_ addObject:cell.user];
  cell.indicator.center = cell.followButton.center;
  cell.followButton.hidden = YES;
  [cell.indicator startAnimating];
  [self sendRelationshipChangeRequestWithPath:kFriendshipCreatePath forUser:cell.user];
}

- (void)unfollowButtonPressed:(id)sender {
  FriendshipTableViewCell* cell = [self friendshipCellFromSubview:sender];
  [followedUsers_ removeObject:cell.user];
  cell.indicator.center = cell.unfollowButton.center;
  cell.unfollowButton.hidden = YES;
  [cell.indicator startAnimating];
  [self sendRelationshipChangeRequestWithPath:kFriendshipRemovePath forUser:cell.user];
}

- (void)connectToTwitterButtonPressed:(id)sender {
  self.signInTwitterConnectButton.enabled = NO;
  [self.signInTwitterActivityIndicator startAnimating];
  // Delay for a half second so the spinner and button have time to visually update.
  [self performSelector:@selector(signInToTwitter) withObject:nil afterDelay:0.0];
}

- (void)connectToFacebookButtonPressed:(id)sender {
  self.signInFacebookConnectButton.enabled = NO;
  [self.signInFacebookActivityIndicator startAnimating];
  // Delay for a half second so the spinner and button have time to visually update.
  [self performSelector:@selector(signInToFacebook) withObject:nil afterDelay:0.0];
}

#pragma mark - Table view data source.

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.findSource == FindFriendsFromContacts)
    return self.contactFriends.count;
  else if (self.findSource == FindFriendsFromTwitter)
    return self.twitterFriends.count;
  else if (self.findSource == FindFriendsFromStamped)
    return self.stampedFriends.count;
  else if (self.findSource == FindFriendsFromFacebook)
    return self.facebookFriends.count;

  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  FriendshipTableViewCell* cell =
      (FriendshipTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[FriendshipTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
    [cell.followButton addTarget:self
                          action:@selector(followButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
    [cell.unfollowButton addTarget:self
                           action:@selector(unfollowButtonPressed:)
                 forControlEvents:UIControlEventTouchUpInside];
  }

  NSArray* friends = nil;
  if (self.findSource == FindFriendsFromTwitter)
    friends = self.twitterFriends;
  else if (self.findSource == FindFriendsFromContacts)
    friends = self.contactFriends;
  else if (self.findSource == FindFriendsFromStamped)
    friends = self.stampedFriends;
  else if (self.findSource == FindFriendsFromFacebook)
    friends = self.facebookFriends;

  User* user = [friends objectAtIndex:indexPath.row];
  cell.followButton.hidden = [followedUsers_ containsObject:user];
  cell.unfollowButton.hidden = !cell.followButton.hidden;
  cell.user = user;
  
  return cell;
}

#pragma mark - Table View Delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  if (findSource_ == FindFriendsFromStamped && !stampedFriends_)
    return 0;
  
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  if (findSource_ == FindFriendsFromStamped && !stampedFriends_)
    return nil;

  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];

  if (findSource_ == FindFriendsFromTwitter && twitterFriends_) {
    if (twitterFriends_.count == 0) {
      view.leftLabel.text = @"No Twitter friends are using Stamped right now.";
      view.rightLabel.text = nil;
    } else {
      view.leftLabel.text = @"Twitter friends using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", twitterFriends_.count];
    }
  } else if (findSource_ == FindFriendsFromContacts && contactFriends_) {
    if (contactFriends_.count == 0) {
      view.leftLabel.text = @"No phone contacts are using Stamped right now.";
      view.rightLabel.text = nil;
    } else {
      view.leftLabel.text = @"Phone contacts using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", contactFriends_.count];
    }
  } else if (findSource_ == FindFriendsFromStamped && stampedFriends_) {
    if (stampedFriends_.count == 0) {
      view.leftLabel.text = @"No friends were found. Sorry :(";
      view.rightLabel.text = nil;
    } else {
      view.leftLabel.text = @"Friends using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", stampedFriends_.count];
    }
  } else if (findSource_ == FindFriendsFromFacebook && facebookFriends_) {
    if (facebookFriends_.count == 0) {
      view.leftLabel.text = @"No Facebook friends are using Stamped right now.";
      view.rightLabel.text = nil;
    } else {
      view.leftLabel.text = @"Facebook friends using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", facebookFriends_.count];
    }
  } else {
    view.leftLabel.text = @"Finding friends who use Stamped...";
    view.rightLabel.text = @"...";
  }
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

  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationCurveEaseOut
                   animations:^{
                     self.nipple.frame = nippleFrame;
                   } completion:nil];
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

- (void)signInToTwitter {

  
  GTMOAuthAuthentication *auth = [self createAuthentication];
  if (auth == nil) {
    NSAssert(NO, @"A valid consumer key and consumer secret are required for signing in to Twitter");
  }

  GTMOAuthViewControllerTouch* authVC =
      [[GTMOAuthViewControllerTouch alloc] initWithScope:kTwitterScope
                                                language:nil
                                         requestTokenURL:[NSURL URLWithString:kTwitterRequestTokenURL]
                                       authorizeTokenURL:[NSURL URLWithString:kTwitterAuthorizeURL]
                                          accessTokenURL:[NSURL URLWithString:kTwitterAccessTokenURL]
                                          authentication:auth
                                          appServiceName:kKeychainTwitterToken
                                                delegate:self
                                        finishedSelector:@selector(viewController:finishedWithAuth:error:)];
  [authVC setBrowserCookiesURL:[NSURL URLWithString:@"http://api.twitter.com/"]];
  [self.signInAuthView addSubview:authVC.view];
  [[authVC webView] setDelegate:self];
  [authVC release];
}

- (void)viewController:(GTMOAuthViewControllerTouch*)authVC
      finishedWithAuth:(GTMOAuthAuthentication*)auth
                 error:(NSError*)error {
  if (error) {
    NSLog(@"GTMOAuth error = %@", error);
    return;
  }
  self.authentication = auth;
  [self fetchCurrentUser];
}


- (void)checkForEndlessSignIn {
  NSLog(@"this works?");
}


#pragma mark - Contacts.

- (void)findStampedFriendsFromEmails:(NSArray*)emails andNumbers:(NSArray*)numbers {
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedEmailFriendsURI
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:[emails componentsJoinedByString:@","] forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
  
  loader = [manager objectLoaderWithResourcePath:kStampedPhoneFriendsURI delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:[numbers componentsJoinedByString:@","] forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
}

#pragma mark - Twitter

- (void)fetchCurrentUser {
  RKRequest* request = [self.twitterClient requestWithResourcePath:kTwitterCurrentUserURI delegate:self];
  request.cachePolicy = RKRequestCachePolicyNone;
  [request prepareURLRequest];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)fetchFriendIDs:(NSString*)userIDString {
  NSString* path =
      [kTwitterFriendsURI appendQueryParams:[NSDictionary dictionaryWithObjectsAndKeys:@"-1", @"cursor", userIDString, @"user_id", nil]];
  RKRequest* request = [self.twitterClient requestWithResourcePath:path delegate:self];
  [self.authentication authorizeRequest:request.URLRequest];
  [request send];
}

- (void)findStampedFriendsFromTwitter:(NSArray*)twitterIDs {
  // TODO: the server only supports 100 IDs at a time. need to chunk.
  if (self.findSource == FindFriendsFromTwitter) {
    self.tableView.hidden = NO;
    [self.signInTwitterActivityIndicator stopAnimating];
    self.signInTwitterConnectButton.enabled = YES;
    self.signInTwitterView.hidden = YES;
  }
  
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];

  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedTwitterFriendsURI
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:[twitterIDs componentsJoinedByString:@","] forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
}

- (void)connectTwitterUserName:(NSString*)username userID:(NSString*)userID {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedLinkedAccountsURI
                                                               delegate:self];
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"twitter_id",
                                                              username, @"twitter_screen_name", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}


#pragma mark - Facebook.

- (void)signInToFacebook {
  if (!self.facebookClient)
    self.facebookClient = ((StampedAppDelegate*)[UIApplication sharedApplication].delegate).facebook;
  
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"] 
      && [defaults objectForKey:@"FBExpirationDateKey"]) {
    self.facebookClient.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
    self.facebookClient.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
  }
  if (!self.facebookClient.isSessionValid) {
    self.facebookClient.sessionDelegate = self;
    [self.facebookClient authorize:[[NSArray alloc] initWithObjects:@"offline_access", nil]];
  }
  if (facebookFriends_) {
    [self.tableView reloadData];
    return;
  }
}

- (void) signOutOfFacebook {
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  if ([defaults objectForKey:@"FBAccessTokenKey"]) {
    [defaults removeObjectForKey:@"FBAccessTokenKey"];
    [defaults removeObjectForKey:@"FBExpirationDateKey"];
    [defaults synchronize];
    
    // Nil out the session variables to prevent
    // the app from thinking there is a valid session
    if (nil != self.facebookClient.accessToken) {
      self.facebookClient.accessToken = nil;
    }
    if (nil != self.facebookClient.expirationDate) {
      self.facebookClient.expirationDate = nil;
    }
    if (self.findSource == FindFriendsFromFacebook)
      self.tableView.hidden = YES;
    self.signInFacebookView.hidden = NO;
    self.signInFacebookConnectButton.enabled = YES;
    [self.signInFacebookActivityIndicator stopAnimating];
  }

}

- (void)fbDidLogin {
  NSLog(@"ok");
  NSUserDefaults* defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:[self.facebookClient accessToken] forKey:@"FBAccessTokenKey"];
  [defaults setObject:[self.facebookClient expirationDate] forKey:@"FBExpirationDateKey"];
  [defaults synchronize];
  [self.facebookClient requestWithGraphPath:@"me" andDelegate:self];
}

- (void)connectFacebookName:(NSString*)name userID:(NSString*)userID {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kStampedLinkedAccountsURI
                                                               delegate:self];
  
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"facebook_id", name, @"facebook_name", nil];
  request.method = RKRequestMethodPOST;
  [request send];
}


// FBRequestDelegate Methods.

- (void)request:(FBRequest*)request didLoad:(id)result {
  NSArray* resultData;
  
  if ([result isKindOfClass:[NSArray class]])
    result = [result objectAtIndex:0];
  if ([result isKindOfClass:[NSDictionary class]]) {
    // handle callback from request for current user info.
    if ([result objectForKey:@"name"]) {
      [self connectFacebookName:[result objectForKey:@"name"] userID:[result objectForKey:@"id"]];
      [self.facebookClient requestWithGraphPath:kFacebookFriendsURI andDelegate:self];
    }
    resultData = [result objectForKey:@"data"];
  }
  
  // handle callback from request for user's friends.
  if (resultData  &&  resultData.count != 0) {
    NSMutableArray* fbFriendIDs = [NSMutableArray array];
    for (NSDictionary* dict in resultData)
      [fbFriendIDs addObject:[dict objectForKey:@"id"]];
    if (fbFriendIDs.count > 0)
      [self findStampedFriendsFromFacebook:fbFriendIDs];
  }
}

- (void) findStampedFriendsFromFacebook:(NSArray*)facebookIDs {
  // TODO: the server only supports 100 IDs at a time. need to chunk.
  if (self.findSource == FindFriendsFromFacebook) {
    [self.signInFacebookActivityIndicator stopAnimating];
    self.signInFacebookConnectButton.enabled = YES;
    self.tableView.hidden = NO;
    self.signInFacebookView.hidden = YES;
  }
  
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedFacebookFriendsURI
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:[facebookIDs componentsJoinedByString:@","] forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
}

- (void)request:(FBRequest*)request didFailWithError:(NSError *)error {
  NSLog(@"FB err code: %d", [error code]);
  NSLog(@"FB err message: %@", [error description]);
  if (error.code == 10000)
    [self signOutOfFacebook];
}

- (void)fbDidNotLogin:(BOOL)cancelled {
  NSLog(@"whoa, no fb login");
  [self signOutOfFacebook];
}


#pragma mark - RKRequestDelegate Methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK) {
    NSLog(@"HTTP error for request: %@, response: %@", request.resourcePath, response.bodyAsString);
    return;
  }

  if ([request.resourcePath isEqualToString:kStampedLinkedAccountsURI]) {
    NSLog(@"Linked account successfully.");
    return;
  }
  
  if ([request.resourcePath isEqualToString:kFriendshipCreatePath] ||
      [request.resourcePath isEqualToString:kFriendshipRemovePath]) {
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
    [self connectTwitterUserName:[body objectForKey:@"screen_name"] userID:[body objectForKey:@"id_str"]];
    // Fetch the list of all the users this user is following.
    [self fetchFriendIDs:[body objectForKey:@"id_str"]];
  }

  // Response for getting Twitter friends. Send on to Stamped to find any
  // Stamped friends.
  else if ([request.resourcePath rangeOfString:kTwitterFriendsURI].location != NSNotFound) {
    [self findStampedFriendsFromTwitter:[body objectForKey:@"ids"]];
    NSLog(@"%@", [body objectForKey:@"ids"]);
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  NSLog(@"Error %@ for request %@", error, request.resourcePath);
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath isEqualToString:kStampedTwitterFriendsURI]) {
    self.twitterFriends =
        [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:
            [NSSortDescriptor sortDescriptorWithKey:@"name" ascending:YES]]];
    [self.tableView reloadData];
  }
  else if ([objectLoader.resourcePath isEqualToString:kStampedFacebookFriendsURI]) {
//    NSLog(@"FB friends on Stamped: %@", objects);
    self.facebookFriends =
    [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:
                                          [NSSortDescriptor sortDescriptorWithKey:@"name" ascending:YES]]];
    [self.tableView reloadData];
  }
  else if ([objectLoader.resourcePath isEqualToString:kStampedPhoneFriendsURI] ||
             [objectLoader.resourcePath isEqualToString:kStampedEmailFriendsURI]) {
    if (objects.count == 0) {
      if (!self.contactFriends) {
        self.contactFriends = objects;
        [self.tableView reloadData];
      }
      return;
    }

    if (!self.contactFriends) {
      self.contactFriends = objects;
    } else {
      self.contactFriends = [self.contactFriends arrayByAddingObjectsFromArray:objects];
      self.contactFriends = [[NSSet setWithArray:self.contactFriends] allObjects];
    }
    self.contactFriends = [self.contactFriends sortedArrayUsingDescriptors:[NSArray arrayWithObject:
        [NSSortDescriptor sortDescriptorWithKey:@"name"
                                      ascending:YES 
                                       selector:@selector(caseInsensitiveCompare:)]]];
    [self.tableView reloadData];
  } else if ([objectLoader.resourcePath isEqualToString:kStampedSearchURI]) {
    self.stampedFriends = objects;
    [self.tableView reloadData];
  } else if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath] ||
             [objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    User* user = [objects objectAtIndex:0];
    NSFetchRequest* request = [Stamp fetchRequest];
    [request setPredicate:[NSPredicate predicateWithFormat:@"user.userID == %@", user.userID]];
    NSArray* results = [Stamp objectsWithFetchRequest:request];
    for (Stamp* s in results)
      s.temporary = [NSNumber numberWithBool:(objectLoader.resourcePath == kFriendshipRemovePath)];

    for (UITableViewCell* cell in tableView_.visibleCells) {
      FriendshipTableViewCell* friendCell = (FriendshipTableViewCell*)cell;
      if (friendCell.user == user) {
        [friendCell.indicator stopAnimating];
        if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath]) {
          friendCell.unfollowButton.hidden = NO;
        } else {
          friendCell.followButton.hidden = NO;
        }
      }
    }

    if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath]) {
      RKObjectManager* objectManager = [RKObjectManager sharedManager];
      RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
      RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:@"/collections/user.json"
                                                                        delegate:self];
      objectLoader.objectMapping = stampMapping;
      objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:@"1", @"quality", user.userID, @"user_id", nil];
      [objectLoader send];
    }
  }
  
  if ([objectLoader.resourcePath rangeOfString:@"/collections/user.json"].location != NSNotFound) {
    for (Stamp* s in objects)
      s.temporary = [NSNumber numberWithBool:NO];
  
    [[(Stamp*)objects.lastObject managedObjectContext] save:NULL];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"Object loader %@ did fail with error %@", objectLoader, error);
  if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath] ||
      [objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    for (UITableViewCell* cell in tableView_.visibleCells) {
      FriendshipTableViewCell* friendCell = (FriendshipTableViewCell*)cell;
      if (friendCell.indicator.isAnimating)
        [friendCell.indicator stopAnimating];
      if ([followedUsers_ containsObject:friendCell.user]) {
        [followedUsers_ removeObject:friendCell.user];
        friendCell.followButton.hidden = NO;
      } else {
        [followedUsers_ addObject:friendCell.user];
        friendCell.unfollowButton.hidden = NO;
      }
    }
  }
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != searchField_)
    return YES;

  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedSearchURI
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:searchField_.text forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
  tableView_.hidden = NO;
  [searchField_ resignFirstResponder];
  return NO;
}

#pragma mark - UIWebViewDelegate Methods.

- (void)webViewDidFinishLoad:(UIWebView *)webView {
  NSString* currentURL = webView.request.URL.absoluteString;
  NSLog(@"%@", currentURL);
  if ([currentURL hasPrefix:@"https://api.twitter.com/oauth/authorize?oauth_token="]) {
    self.signInAuthView.alpha = 0.0;
    self.signInAuthView.hidden = NO;
    [UIView animateWithDuration:0.25
                     animations:^{signInAuthView_.alpha = 1.0;}];   /*
                     completion:^(BOOL finished){
                       [UIView animateWithDuration:0.5
                                             delay:1.0
                                           options:UIViewAnimationOptionAllowUserInteraction
                                        animations:^{webView.scrollView.contentOffset = CGPointMake(0.0, 140.0);}
                                        completion:nil];}];         */
  }
}

@end
