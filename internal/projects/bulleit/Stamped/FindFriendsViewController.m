//
//  FindFriendsViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "FindFriendsViewController.h"

#import <AddressBook/AddressBook.h>

#import "GTMOAuthAuthentication.h"
#import "GTMOAuthViewControllerTouch.h"

#import "FBConnect.h"

#import "STSectionHeaderView.h"
#import "FriendshipTableViewCell.h"
#import "Util.h"
#import "User.h"

static NSString* const kTwitterCurrentUserURI = @"/account/verify_credentials.json";
static NSString* const kTwitterFriendsURI = @"/friends/ids.json";
static NSString* const kStampedTwitterFriendsURI = @"/users/find/twitter.json";
static NSString* const kStampedEmailFriendsURI = @"/users/find/email.json";
static NSString* const kStampedPhoneFriendsURI = @"/users/find/phone.json";
static NSString* const kStampedLinkedAccountsURI = @"/account/linked_accounts.json";
static NSString* const kFriendshipCreatePath = @"/friendships/create.json";
static NSString* const kFriendshipRemovePath = @"/friendships/remove.json";

@interface FindFriendsViewController ()
- (void)adjustNippleToView:(UIView*)view;
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
- (void)fetchCurrentUser;
- (void)fetchFriendIDs:(NSString*)userIDString;
- (void)findStampedFriendsFromTwitter:(NSArray*)twitterIDs;
- (void)findStampedFriendsFromEmails:(NSArray*)emails andNumbers:(NSArray*)numbers;

@property (nonatomic, assign) FindFriendsSource findSource;
@property (nonatomic, retain) GTMOAuthAuthentication* authentication;
@property (nonatomic, retain) RKClient* twitterClient;
@property (nonatomic, copy) NSArray* twitterFriends;
@property (nonatomic, copy) NSArray* contactFriends;
@end

@implementation FindFriendsViewController

@synthesize findSource = findSource_;
@synthesize authentication = authentication_;
@synthesize twitterClient = twitterClient_;
@synthesize twitterFriends = twitterFriends_;
@synthesize contactFriends = contactFriends_;
@synthesize followedUsers = followedUsers_;

@synthesize contactsButton = contactsButton_;
@synthesize twitterButton = twitterButton_;
@synthesize nipple = nipple_;
@synthesize tableView = tableView_;


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
  self.nipple = nil;
  self.tableView = nil;
  [super dealloc];
}

#pragma mark - View Lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.twitterClient = [RKClient clientWithBaseURL:@"http://api.twitter.com/1"];
  if (self.findSource == FindFriendsFromContacts)
    [self findFromContacts:self];
  else if (self.findSource == FindFriendsFromTwitter)
    [self findFromTwitter:self];
}

- (void)viewDidUnload {
  self.twitterClient = nil;
  self.twitterFriends = nil;
  self.contactFriends = nil;
  self.contactsButton = nil;
  self.twitterButton = nil;
  self.nipple = nil;
  self.tableView = nil;

  [super viewDidUnload];
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
  for (NSString* num in allNumbers)
    [sanitizedNumbers addObject:[Util sanitizedPhoneNumberFromString:num]];

  [self findStampedFriendsFromEmails:allEmails andNumbers:sanitizedNumbers];
}

- (IBAction)findFromTwitter:(id)sender {
  [self.contactsButton setImage:[UIImage imageNamed:@"contacts_icon_disabled"]
                       forState:UIControlStateNormal];
  [self.twitterButton setImage:[UIImage imageNamed:@"twitter_logo"]
                      forState:UIControlStateNormal];
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
    [self signInToTwitter];
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

#pragma mark - Table view data source.

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.findSource == FindFriendsFromContacts)
    return self.contactFriends.count;
  else if (self.findSource == FindFriendsFromTwitter)
    return self.twitterFriends.count;

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

  User* user = [friends objectAtIndex:indexPath.row];
  cell.followButton.hidden = [followedUsers_ containsObject:user];
  cell.unfollowButton.hidden = !cell.followButton.hidden;
  cell.user = user;
  
  return cell;
}

#pragma mark - Table View Delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
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
  NSString *myConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
  NSString *myConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";

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
  NSString* html = @"<html><body style='background-image:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAMAAACelLz8AAAAq1BMVEXm5uXp6unm5ubm5ebp6erl5ebk5OTk5OPn5+fo5+fl5eXp6eno5+jq6erj4uLo6ejo6Onl5ubp6Onn6Ojn5ufo6eni4uLi4+Pq6unm5eXj4+Pk5eTk5eXk4+To6Ojl5eTl5OTn5+bk5OXj5OPn5+jj4uPm5+fl5OXj5OTm5ufi4+Lk4+Pn6Ofn5ubp6ejp6Ojq6enm5+bj4+Lq6uro6Ofl5uXp6uri4uPj4+RSUFBuAAACFklEQVQYGQXBC4KCIBQAwBcmIJj5L0Hwm2Kapmnb/U+2MwAnZJ1tGxNqOYwT9+JdfdcOwsiBOInT2z0TMsdKa3ErSiFTESG/Ag12WBdNG9Yi0po+eNL1NiDvkgDzDdHJaXhSxEeT12nBJv1yZFZDS19hOqPMHi7lYnNWvF1d9mG7KsD5VbGBY+neO7a99Icn6W4wZ2/Yypo0TxSEtvTVY7EVbth5i4kvAI2n8WysyTrMeHravkWPlRBzUAbsLbX/naxd2e2WbqWZPbRUz0p4MGdzR2scSqXldHNfaZ9lnyh/5xs0gcHqir9TNePWxHSosIzN9rduYMnTVVCR1imuBjr3GE1Y97HxBngOgcBRna5os0QWeETNQUsFnySYlQ2tdlxiogn7zlLsykg+dbcvvB2a34/xd21E/JvtfqPaRVG/fxMQK5VLKKqHrH4BCaJD010d9Dc84Gfu0WQ6c2msFHVFz5cd4WBgXgnttPQZFjQWHbpnxyMc84T5J5QzoGsypO3O+MpbZSw9R6hCsdafB/zMrrhafFmJt1vGInbUfilUfu+g2uLCOgKceBsJDGo82c9G4PMLw84evjPP17XztVIjr3U+D05HVwxIh/hnW3ciuMFbFXwplgbv5NwDwqbzut5C0ITen7FUJdKeaTGOQISmxcUXE0NLvgqHNevgwrt1CSQ7lbq7ttTJtjDRtN+POug+gy7/AT1WRIG2q/GCAAAAAElFTkSuQmCC);font:14px Helvetica-Bold;color:#666;text-shadow:#fff 0px 1px'><div style='padding-top:180px;' align=center>Loading Twitter sign-in page...</div></body></html>";
  [authVC setInitialHTMLString:html];
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
  self.authentication = auth;
  [self fetchCurrentUser];
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
  } else if ([objectLoader.resourcePath isEqualToString:kStampedPhoneFriendsURI] ||
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
      self.contactFriends = [self.contactFriends valueForKeyPath:@"@distinctUnionOfObjects.userID"];
    }
    self.contactFriends = [self.contactFriends sortedArrayUsingDescriptors:[NSArray arrayWithObject:
        [NSSortDescriptor sortDescriptorWithKey:@"name"
                                      ascending:YES 
                                       selector:@selector(caseInsensitiveCompare:)]]];
    [self.tableView reloadData];
  } else if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath] ||
             [objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    User* user = [objects objectAtIndex:0];
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

@end
