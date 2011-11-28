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

#import "AccountManager.h"
#import "STSectionHeaderView.h"
#import "STNavigationBar.h"
#import "STSearchField.h"
#import "FriendshipTableViewCell.h"
#import "FriendshipManager.h"
#import "InviteFriendTableViewCell.h"
#import "ProfileViewController.h"
#import "Stamp.h"
#import "SuggestedUserTableViewCell.h"
#import "Util.h"
#import "User.h"
#import "UserImageView.h"
#import "Alerts.h"
#import "SocialManager.h"

static NSString* const kStampedEmailFriendsURI = @"/users/find/email.json";
static NSString* const kStampedPhoneFriendsURI = @"/users/find/phone.json";
static NSString* const kStampedSearchURI = @"/users/search.json";
static NSString* const kStampedSuggestedUsersURI = @"/users/suggested.json";
static NSString* const kFriendshipCreatePath = @"/friendships/create.json";
static NSString* const kFriendshipRemovePath = @"/friendships/remove.json";
static NSString* const kInvitePath = @"/friendships/invite.json";

@interface FindFriendsViewController () 
- (void)adjustNippleToView:(UIView*)view;
- (void)setSearchFieldHidden:(BOOL)hidden animated:(BOOL)animated;
- (void)sendRelationshipChangeRequestWithPath:(NSString*)path forUser:(User*)user;
- (void)followButtonPressed:(id)sender;
- (void)unfollowButtonPressed:(id)sender;
- (void)inviteButtonPressed:(id)sender;
- (UITableViewCell*)cellFromSubview:(UIView*)view;
- (void)findStampedFriendsFromEmails:(NSArray*)emails andNumbers:(NSArray*)numbers;
- (void)loadSuggestedUsers;
- (void)removeUsersToInviteWithIdentifers:(NSArray*)identifiers;
- (void)sendInviteRequestToEmail:(NSString*)email;
- (void)socialNetworksDidChange:(NSNotification*)note;
- (void)twitterFriendsDidChange:(NSNotification*)note;
- (void)facebookFriendsDidChange:(NSNotification*)note;

@property (nonatomic, assign) FindFriendsSource findSource;
@property (nonatomic, copy) NSArray* twitterFriends;
@property (nonatomic, copy) NSArray* contactFriends;
@property (nonatomic, copy) NSArray* stampedFriends;
@property (nonatomic, copy) NSArray* facebookFriends;
@property (nonatomic, copy) NSArray* suggestedFriends;
@property (nonatomic, retain) NSMutableArray* contactsNotUsingStamped;
@property (nonatomic, retain) NSMutableArray* invitedContacts;
@property (nonatomic, assign) BOOL searchFieldHidden;
@end

@implementation FindFriendsViewController

@synthesize findSource = findSource_;
@synthesize twitterFriends = twitterFriends_;
@synthesize contactFriends = contactFriends_;
@synthesize stampedFriends = stampedFriends_;
@synthesize suggestedFriends = suggestedFriends_;
@synthesize facebookFriends = facebookFriends_;
@synthesize contactsNotUsingStamped = contactsNotUsingStamped_;
@synthesize invitedContacts = invitedContacts_;
@synthesize contactsButton = contactsButton_;
@synthesize twitterButton = twitterButton_;
@synthesize facebookButton = facebookButton_;
@synthesize stampedButton = stampedButton_;
@synthesize searchField = searchField_;
@synthesize nipple = nipple_;
@synthesize tableView = tableView_;
@synthesize searchFieldHidden = searchFieldHidden_;
@synthesize signInTwitterView = signInTwitterView_;
@synthesize signInFacebookView = signInFacebookView_;
@synthesize signInTwitterActivityIndicator = signInTwitterActivityIndicator_;
@synthesize signInFacebookActivityIndicator = signInFacebookActivityIndicator_;
@synthesize signInTwitterConnectButton = signinTwitterConnectButton_;
@synthesize signInFacebookConnectButton = signInFacebookConnectButton_;
@synthesize inviteViaEmailButton = inviteViaEmailButton_;

- (id)initWithFindSource:(FindFriendsSource)source {
  if ((self = [self initWithNibName:@"FindFriendsView" bundle:nil])) {
    self.findSource = source;
  }
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.twitterFriends = nil;
  self.contactFriends = nil;
  self.suggestedFriends = nil;
  self.contactsNotUsingStamped = nil;
  self.invitedContacts = nil;
  self.contactsButton = nil;
  self.twitterButton = nil;
  self.facebookButton = nil;
  self.stampedButton = nil;
  self.searchField = nil;
  self.nipple = nil;
  self.tableView = nil;
  self.signInTwitterView = nil;
  self.signInFacebookView = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
  self.signInTwitterConnectButton = nil;
  self.signInFacebookConnectButton = nil;
  self.inviteViaEmailButton = nil;
  
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  
  [super dealloc];
}

#pragma mark - View Lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  [self.tableView reloadData];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)didDisplayAsModal {
//  [self socialNetworksDidChange:nil];
  if (self.findSource == FindFriendsSourceTwitter)
    [self findFromTwitter:self];
  else if (self.findSource == FindFriendsSourceFacebook)
    [self findFromFacebook:self];
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    [[Alerts alertWithTemplate:AlertTemplateNoInternet] show];
  [self findFromStamped:self];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.invitedContacts = [NSMutableArray array];
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Add Friends"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
  searchFieldHidden_ = YES;
  
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(socialNetworksDidChange:)
                                               name:kSocialNetworksChangedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(twitterFriendsDidChange:)
                                               name:kTwitterFriendsChangedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(facebookFriendsDidChange:)
                                               name:kFacebookFriendsChangedNotification
                                             object:nil];
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable)
    [self loadSuggestedUsers];

  if (self.findSource == FindFriendsSourceStamped)
    [self findFromStamped:self];
  else if (self.findSource == FindFriendsSourceContacts)
    [self findFromContacts:self];
  else if (self.findSource == FindFriendsSourceTwitter)
    [self findFromTwitter:self];
  else if (self.findSource == FindFriendsSourceFacebook)
    [self findFromFacebook:self];
  else
    [self findFromStamped:self];
  
  inviteViaEmailButton_.enabled = [MFMailComposeViewController canSendMail];
}

- (void)viewDidUnload {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];

  self.twitterFriends = nil;
  self.contactFriends = nil;
  self.contactsButton = nil;
  self.twitterButton = nil;
  self.facebookButton = nil;
  self.stampedButton = nil;
  self.suggestedFriends = nil;
  self.contactsNotUsingStamped = nil;
  self.invitedContacts = nil;
  self.nipple = nil;
  self.searchField = nil;
  self.tableView = nil;
  self.signInTwitterView = nil;
  self.signInFacebookView = nil;
  self.signInTwitterActivityIndicator = nil;
  self.signInFacebookActivityIndicator = nil;
  self.signInTwitterConnectButton = nil;
  self.signInFacebookConnectButton = nil;
  self.inviteViaEmailButton = nil;

  [[NSNotificationCenter defaultCenter] removeObserver:self]; 

  [super viewDidUnload];
}

#pragma mark - MFMailComposeViewControllerDelegate methods.

- (void)mailComposeController:(MFMailComposeViewController*)controller
          didFinishWithResult:(MFMailComposeResult)result
                        error:(NSError*)error {
  [self dismissModalViewControllerAnimated:YES];
}

#pragma mark - Actions

- (IBAction)inviteFriendViaEmail:(id)sender {
  MFMailComposeViewController* vc = [[MFMailComposeViewController alloc] init];
  vc.mailComposeDelegate = self;
  [vc setSubject:@"Check out Stamped."];
  [vc setMessageBody:@"I'm using Stamped, a new way to recommend only what you like best. You should check it out by downloading the iPhone app here:<br/><br/><a href=\"http://stamped.com/download\">stamped.com/download</a>" isHTML:YES];
  [self presentModalViewController:vc animated:YES];
  [vc release];
}

- (IBAction)done:(id)sender {
  UIViewController* vc = nil;
  if ([self respondsToSelector:@selector(presentingViewController)])
    vc = [(id)self presentingViewController];
  else
    vc = self.parentViewController;

  [vc dismissModalViewControllerAnimated:YES];
}

- (IBAction)findFromStamped:(id)sender {
  self.findSource = FindFriendsSourceSuggested;
  [self setSearchFieldHidden:NO animated:NO];
  [self adjustNippleToView:self.stampedButton];
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable) {
    if (!suggestedFriends_ || suggestedFriends_.count == 0)
      [self loadSuggestedUsers];
  }

  tableView_.hidden = NO;
  signInTwitterView_.hidden = YES;
  signInFacebookView_.hidden = YES;
  self.stampedFriends = nil;
  contactsButton_.selected = NO;
  twitterButton_.selected = NO;
  facebookButton_.selected = NO;
  stampedButton_.selected = YES;
  
  [tableView_ reloadData];
}

- (IBAction)findFromContacts:(id)sender {
  self.findSource = FindFriendsSourceContacts;
  [self adjustNippleToView:self.contactsButton];
  [searchField_ resignFirstResponder];
  [self setSearchFieldHidden:YES animated:NO];
  self.signInTwitterView.hidden = YES;
  self.signInFacebookView.hidden = YES;
  tableView_.hidden = NO;
  contactsButton_.selected = YES;
  twitterButton_.selected = NO;
  facebookButton_.selected = NO;
  stampedButton_.selected = NO;
  if (contactFriends_) {
    [self.tableView reloadData];
    return;
  }
  [tableView_ reloadData];
  // Fetch the address book 
  // Perform this on the next cycle to avoid a hang when tapping the Contacts button.
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 0.1 * NSEC_PER_SEC), dispatch_get_current_queue(), ^{
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
    RKClient* client = [RKClient sharedClient];
    if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable)
      [self findStampedFriendsFromEmails:allEmails andNumbers:sanitizedNumbers];
    [tableView_ reloadData];
  });
}

- (IBAction)findFromTwitter:(id)sender {
  self.findSource = FindFriendsSourceTwitter;
  
  [self adjustNippleToView:self.twitterButton];
  [searchField_ resignFirstResponder];
  [self setSearchFieldHidden:YES animated:NO];
  [self.tableView reloadData];
  tableView_.hidden = NO;
  contactsButton_.selected = NO;
  twitterButton_.selected = YES;
  facebookButton_.selected = NO;
  stampedButton_.selected = NO;
    
  if ([[SocialManager sharedManager] isSignedInToTwitter]) {
    self.signInTwitterView.hidden = YES;
    [[SocialManager sharedManager] refreshStampedFriendsFromTwitter];
  } 
  else {
    self.tableView.hidden = YES;
    self.signInFacebookView.hidden = YES;
    self.signInTwitterView.hidden = NO;
  }
}

- (IBAction)findFromFacebook:(id)sender {
  self.findSource = FindFriendsSourceFacebook;
  [self adjustNippleToView:facebookButton_];
  [searchField_ resignFirstResponder];
  [self setSearchFieldHidden:YES animated:NO];
  [self.tableView reloadData];
  tableView_.hidden = NO;
  contactsButton_.selected = NO;
  twitterButton_.selected = NO;
  facebookButton_.selected = YES;
  stampedButton_.selected = NO;

  if ([[SocialManager sharedManager] isSignedInToFacebook]) {
    self.signInFacebookView.hidden = YES;
    [[SocialManager sharedManager] refreshStampedFriendsFromFacebook];
  }
  else {
    self.tableView.hidden = YES;
    self.signInFacebookView.hidden = NO;
    self.signInTwitterView.hidden = YES;
    return;
  }
}

- (void)loadSuggestedUsers {
  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedSuggestedUsersURI
                                                        delegate:self];
  loader.objectMapping = mapping;
  [loader send];
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

- (UITableViewCell*)cellFromSubview:(UIView*)view {
  UIView* superview = view.superview;
  while (superview && (![superview isMemberOfClass:[FriendshipTableViewCell class]] &&
                       ![superview isMemberOfClass:[SuggestedUserTableViewCell class]] &&
                       ![superview isMemberOfClass:[InviteFriendTableViewCell class]])) {
    superview = superview.superview;
  }
  return (UITableViewCell*)superview;
}

- (void)sendInviteRequestToEmail:(NSString*)email {
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kInvitePath delegate:nil];
  request.method = RKRequestMethodPOST;
  request.params = [NSDictionary dictionaryWithObject:email forKey:@"email"];
  [request send];
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
  UITableViewCell* cell = [self cellFromSubview:sender];
  User* user = (User*)[(id)cell user];
  [(id)cell indicator].center = [(id)cell followButton].center;
  [(id)cell followButton].hidden = YES;
  [[(id)cell indicator] startAnimating];
  User* currentUser = [AccountManager sharedManager].currentUser;
  [currentUser addFollowingObject:user];
  [self sendRelationshipChangeRequestWithPath:kFriendshipCreatePath forUser:user];
}

- (void)unfollowButtonPressed:(id)sender {
  UITableViewCell* cell = [self cellFromSubview:sender];
  User* user = (User*)[(id)cell user];
  [(id)cell indicator].center = [(id)cell unfollowButton].center;
  [(id)cell unfollowButton].hidden = YES;
  [[(id)cell indicator] startAnimating];
  User* currentUser = [AccountManager sharedManager].currentUser;
  [currentUser removeFollowingObject:user];
  [self sendRelationshipChangeRequestWithPath:kFriendshipRemovePath forUser:user];
}

- (void)inviteButtonPressed:(id)sender {
  UIButton* button = sender;

  button.enabled = NO;
  InviteFriendTableViewCell* cell = (InviteFriendTableViewCell*)[self cellFromSubview:sender];
  NSString* email = cell.emailLabel.text;
  if (![invitedContacts_ containsObject:email])
    [invitedContacts_ addObject:email];
  [self sendInviteRequestToEmail:email];
}

- (void)connectToTwitterButtonPressed:(id)sender {
  self.signInTwitterConnectButton.enabled = NO;
  [self.signInTwitterActivityIndicator startAnimating];
  // Delay for a half second so the spinner and button have time to visually update.
  [[SocialManager sharedManager] performSelector:@selector(signInToTwitter:) withObject:self.navigationController afterDelay:0.35];
}

- (void)connectToFacebookButtonPressed:(id)sender {
  self.signInFacebookConnectButton.enabled = NO;
  [self.signInFacebookActivityIndicator startAnimating];
  // Delay for a half second so the spinner and button have time to visually update.
  [[SocialManager sharedManager] performSelector:@selector(signInToFacebook) withObject:nil afterDelay:0.35];
}

- (void)socialNetworksDidChange:(NSNotification*)note {
  [tableView_ reloadData];
  // Twitter
  if ([[SocialManager sharedManager] isSignedInToTwitter]) {
    // If we're watching, fade in the table.
    if (self.findSource == FindFriendsSourceTwitter && !self.signInTwitterView.hidden
        && twitterFriends_) {
      [self setSearchFieldHidden:YES animated:NO];
      self.tableView.alpha = 0.0;
      self.tableView.hidden = NO;
      [UIView animateWithDuration:0.4
                       animations:^{self.tableView.alpha = 1.0;}
                       completion:^(BOOL finished){
                         self.signInTwitterView.hidden = YES;
                         [self.signInTwitterActivityIndicator stopAnimating];
                         self.signInTwitterConnectButton.enabled = YES;
                       }];
    }
    // Otherwise, just make sure the table isn't hidden.
    else if (!self.signInTwitterView.hidden && twitterFriends_) {
      self.signInTwitterView.hidden = YES;
      [self.signInTwitterActivityIndicator stopAnimating];
      self.signInTwitterConnectButton.enabled = YES;
    }
  }
  else {
    self.twitterFriends = nil;
    [self.signInTwitterActivityIndicator stopAnimating];
    self.signInTwitterConnectButton.enabled = YES;
    // If we're watching, fade out the table.
    if (self.findSource == FindFriendsSourceTwitter && self.tableView.hidden == NO) {
      self.searchFieldHidden = YES;
      self.signInTwitterView.hidden = NO;
      self.signInFacebookView.hidden = YES;
      [UIView animateWithDuration:0.4
                       animations:^{ self.tableView.alpha = 0.0; }
                       completion:^(BOOL finished) {
                         self.tableView.hidden = YES;
                         self.tableView.alpha = 1.0;
                       }];
    }
    // Otherwise, just make sure the table is hidden.
//    else
//      self.signInTwitterView.hidden = NO;
  }

  
  // Facebook
  if ([[SocialManager sharedManager] isSignedInToFacebook]) {
    if (self.findSource == FindFriendsSourceFacebook && !self.signInFacebookView.hidden
        && facebookFriends_) {
      [self setSearchFieldHidden:YES animated:NO];
      self.tableView.alpha = 0.0;
      self.tableView.hidden = NO;
      [UIView animateWithDuration:0.4
                       animations:^{self.tableView.alpha = 1.0;}
                       completion:^(BOOL finished){
                         self.signInFacebookView.hidden = YES;
                         [self.signInFacebookActivityIndicator stopAnimating];
                         self.signInFacebookConnectButton.enabled = YES;
                       }];
    }
    else if (!self.signInFacebookView.hidden && facebookFriends_) {
      self.signInFacebookView.hidden = YES;
      [self.signInFacebookActivityIndicator stopAnimating];
      self.signInFacebookConnectButton.enabled = YES;
    }
  }
  else {
    self.facebookFriends = nil;
    [self.signInFacebookActivityIndicator stopAnimating];
    self.signInFacebookConnectButton.enabled = YES;
    if (self.findSource == FindFriendsSourceFacebook && self.tableView.hidden == NO) {
      self.searchFieldHidden = YES;
      self.signInFacebookView.hidden = NO;
      self.signInTwitterView.hidden = YES;
      [UIView animateWithDuration:0.4
                       animations:^{ self.tableView.alpha = 0.0; }
                       completion:^(BOOL finished) {
                         self.tableView.hidden = YES;
                         self.tableView.alpha = 1.0;
                       }];
    }
//    else
//      self.signInFacebookView.hidden = NO;
  }
}

- (void)twitterFriendsDidChange:(NSNotification*)note {
  if (note.object && [note.object isKindOfClass:[NSArray class]])
    self.twitterFriends = note.object;
  [self.tableView reloadData];
  [self socialNetworksDidChange:nil];
}

- (void)facebookFriendsDidChange:(NSNotification*)note {
  if (note.object && [note.object isKindOfClass:[NSArray class]])
    self.facebookFriends = note.object;
  [self.tableView reloadData];
  [self socialNetworksDidChange:nil];
}

#pragma mark - Table view data source.

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  if (findSource_ == FindFriendsSourceContacts && contactsNotUsingStamped_.count > 0)
    return 2;
  return 1;
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (findSource_ == FindFriendsSourceSuggested) {
    User* user = [suggestedFriends_ objectAtIndex:indexPath.row];
    CGSize bioSize = [user.bio sizeWithFont:[UIFont fontWithName:@"Helvetica" size:12]
                          constrainedToSize:CGSizeMake(300, MAXFLOAT)
                              lineBreakMode:UILineBreakModeWordWrap];
    return bioSize.height + 83;
  }
  return 51.0;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.findSource == FindFriendsSourceContacts) {
    if (section == 0)
      return self.contactFriends.count;
    else if (section == 1)
      return contactsNotUsingStamped_.count;
  }
  else if (self.findSource == FindFriendsSourceTwitter)
    return self.twitterFriends.count;
  else if (self.findSource == FindFriendsSourceStamped)
    return self.stampedFriends.count;
  else if (self.findSource == FindFriendsSourceSuggested)
    return self.suggestedFriends.count;
  else if (self.findSource == FindFriendsSourceFacebook)
    return self.facebookFriends.count;

  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  NSString* CellIdentifier = findSource_ == FindFriendsSourceSuggested ? @"SuggestedCell" : @"FriendshipCell";
  if (findSource_ == FindFriendsSourceContacts && indexPath.section == 1)
    CellIdentifier = @"InviteCell";

  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    if (findSource_ == FindFriendsSourceContacts && indexPath.section == 1) {
      cell = [[[InviteFriendTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
      [[(id)cell inviteButton] addTarget:self
                                  action:@selector(inviteButtonPressed:)
                        forControlEvents:UIControlEventTouchUpInside];
    } else {
      if (findSource_ == FindFriendsSourceSuggested)
        cell = [[[SuggestedUserTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
      else
        cell = [[[FriendshipTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];

      [[(id)cell followButton] addTarget:self
                                  action:@selector(followButtonPressed:)
                        forControlEvents:UIControlEventTouchUpInside];
      [[(id)cell unfollowButton] addTarget:self
                                    action:@selector(unfollowButtonPressed:)
                          forControlEvents:UIControlEventTouchUpInside];
    }
  }

  if (findSource_ == FindFriendsSourceContacts && indexPath.section == 1) {
    ABRecordRef person = [contactsNotUsingStamped_ objectAtIndex:indexPath.row];
    InviteFriendTableViewCell* inviteCell = (InviteFriendTableViewCell*)cell;
    CFStringRef name = ABRecordCopyCompositeName(person);
    if (name) {
      inviteCell.nameLabel.text = (NSString*)name;
      CFRelease(name);
    } else {
      inviteCell.nameLabel.text = nil;
    }

    inviteCell.inviteButton.enabled = YES;
    ABMultiValueRef emailProperty = ABRecordCopyValue(person, kABPersonEmailProperty);
    NSArray* emails = (NSArray*)ABMultiValueCopyArrayOfAllValues(emailProperty);
    CFRelease(emailProperty);
    if (emails.count > 0) {
      NSString* email = [emails objectAtIndex:0];
      inviteCell.emailLabel.text = email;
      if ([invitedContacts_ containsObject:email])
        inviteCell.inviteButton.enabled = NO;
    }
    [emails release];
    if (ABPersonHasImageData(person)) {
      CFDataRef imageData = ABPersonCopyImageData(person);
      inviteCell.userImageView.imageView.image = [UIImage imageWithData:(NSData*)imageData];
      CFRelease(imageData);
    }
  } else {
    NSArray* friends = nil;
    if (self.findSource == FindFriendsSourceTwitter)
      friends = self.twitterFriends;
    else if (self.findSource == FindFriendsSourceContacts)
      friends = self.contactFriends;
    else if (self.findSource == FindFriendsSourceStamped)
      friends = self.stampedFriends;
    else if (self.findSource == FindFriendsSourceSuggested)
      friends = self.suggestedFriends;
    else if (self.findSource == FindFriendsSourceFacebook)
      friends = self.facebookFriends;

    User* user = [friends objectAtIndex:indexPath.row];
    User* currentUser = [AccountManager sharedManager].currentUser;
    [(id)cell followButton].hidden = [currentUser.following containsObject:user];
    [(id)cell unfollowButton].hidden = ![(id)cell followButton].hidden;
    [(id)cell setUser:user];
  }
  return cell;
}

#pragma mark - Table View Delegate

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
  return 25;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
  STSectionHeaderView* view = [[[STSectionHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 25)] autorelease];

  if (findSource_ == FindFriendsSourceTwitter && twitterFriends_) {
    if (twitterFriends_.count == 0) {
      view.leftLabel.text = @"No Twitter friends are using Stamped.";
      view.rightLabel.text = @":(";
    } else {
      view.leftLabel.text = @"Twitter friends using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", twitterFriends_.count];
    }
  } else if (findSource_ == FindFriendsSourceContacts && contactFriends_) {
    if (section == 0) {
      if (contactFriends_.count == 0) {
        view.leftLabel.text = @"No phone contacts are using Stamped.";
        view.rightLabel.text = @":(";
      } else {
        view.leftLabel.text = @"Phone contacts using Stamped";
        view.rightLabel.text = [NSString stringWithFormat:@"%u", contactFriends_.count];
      }
    } else if (section == 1) {
      if (contactsNotUsingStamped_.count == 0) {
        return nil;
      } else {
        view.leftLabel.text = @"Phone contacts not using Stamped";
        view.rightLabel.text = [NSString stringWithFormat:@"%u", contactsNotUsingStamped_.count];
      }
    }
  } else if (findSource_ == FindFriendsSourceStamped && stampedFriends_) {
    if (stampedFriends_.count == 0) {
      view.leftLabel.text = @"No results.";
      view.rightLabel.text = @":(";
    } else {
      view.leftLabel.text = @"Stamped users";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", stampedFriends_.count];
    }
  } else if (findSource_ == FindFriendsSourceFacebook && facebookFriends_) {
    if (facebookFriends_.count == 0) {
      view.leftLabel.text = @"No Facebook friends are using Stamped.";
      view.rightLabel.text = @":(";
    } else {
      view.leftLabel.text = @"Facebook friends using Stamped";
      view.rightLabel.text = [NSString stringWithFormat:@"%u", facebookFriends_.count];
    }
  } else if (findSource_ == FindFriendsSourceFacebook && !facebookFriends_) {
      view.leftLabel.text = @"Finding friends who use Stamped…";
      view.rightLabel.text = nil;
  } else if (findSource_ == FindFriendsSourceTwitter && !twitterFriends_) {
      view.leftLabel.text = @"Finding friends who use Stamped…";
      view.rightLabel.text = nil;
  } else if (findSource_ == FindFriendsSourceContacts && !contactFriends_) {
      view.leftLabel.text = @"Finding friends who use Stamped…";
      view.rightLabel.text = nil;
  } else if (findSource_ == FindFriendsSourceStamped) {
      view.leftLabel.text = @"Finding friends who use Stamped…";
      view.rightLabel.text = @"…";
  } else if (findSource_ == FindFriendsSourceSuggested) {
    view.leftLabel.text = @"Suggested Users";
    view.rightLabel.text = @"";
  }
  return view;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  UITableViewCell* cell = [tableView_ cellForRowAtIndexPath:indexPath];
  if ([cell isMemberOfClass:[FriendshipTableViewCell class]] ||
      [cell isMemberOfClass:[SuggestedUserTableViewCell class]]) {
    User* user = (User*)[(id)cell user];
    ProfileViewController* vc = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController"
                                                                        bundle:nil];
    vc.user = user;
    [self.navigationController pushViewController:vc animated:YES];
    [vc release];
  }
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
    if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound) {
      // Error catching.
      switch (response.statusCode) {
        case 400:
        case 500: {
          [[Alerts alertWithTemplate:AlertTemplateDefault] show];
          break;
        }
        case 200: {
          UIAlertView* alertView = [[UIAlertView alloc] initWithTitle:@"Already Following"
                                                              message:@""
                                                             delegate:nil
                                                    cancelButtonTitle:@"Fair Enough"
                                                    otherButtonTitles:nil];
          NSError* err = nil;
          NSString* username = nil;
          id body = [response parsedBody:&err];
          if (!err) {
            username = [body objectForKey:@"username"];
          }
          alertView.title = @"Already Following";
          if (username)
            alertView.message = [NSString stringWithFormat: @"You're already following %@.", username];
          else 
            alertView.message = @"You're already following that person.";
          [alertView show];
          [alertView release];
          break;
        }
        default:
          break;
      }
      return;
    }
    if ([request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound) {
      [[Alerts alertWithTemplate:AlertTemplateDefault] show];
      return;
    }
    
    NSLog(@"HTTP error for request: %@, response: %@", request.resourcePath, response.bodyAsString);
    return;
  }
    
  if ([request.resourcePath isEqualToString:kFriendshipCreatePath] ||
      [request.resourcePath isEqualToString:kFriendshipRemovePath]) {
    return;
  }
}

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound)
    [[Alerts alertWithTemplate:AlertTemplateDefault] show];
  NSLog(@"Error %@ for request %@", error, request.resourcePath);

}

- (void)requestDidTimeout:(RKRequest *)request {
  if ([request.resourcePath rangeOfString:kFriendshipCreatePath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kFriendshipRemovePath].location != NSNotFound)
    [[Alerts alertWithTemplate:AlertTemplateTimedOut] show];
}

- (void)requestDidCancelLoad:(RKRequest *)request {
  return;
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSSortDescriptor* sortDescriptor = [NSSortDescriptor sortDescriptorWithKey:@"name"
                                                                   ascending:YES 
                                                                    selector:@selector(localizedCaseInsensitiveCompare:)];

  if ([objectLoader.resourcePath isEqualToString:kStampedPhoneFriendsURI] ||
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
    } 
    else {
      self.contactFriends = [self.contactFriends arrayByAddingObjectsFromArray:objects];
      self.contactFriends = [[NSSet setWithArray:self.contactFriends] allObjects];
    }
    self.contactFriends = [self.contactFriends sortedArrayUsingDescriptors:[NSArray arrayWithObject:sortDescriptor]];
    [self removeUsersToInviteWithIdentifers:[objects valueForKeyPath:@"@distinctUnionOfObjects.identifier"]];
    [self.tableView reloadData];
  }
  
  else if ([objectLoader.resourcePath isEqualToString:kStampedSearchURI]) {
    self.stampedFriends = objects;
    [self.tableView reloadData];
  }
  
  else if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath] ||
           [objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    User* user = [objects objectAtIndex:0];
    if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath])
      [[FriendshipManager sharedManager] followUser:user];
    else
      [[FriendshipManager sharedManager] unfollowUser:user];

    for (UITableViewCell* cell in tableView_.visibleCells) {
      if (![cell isMemberOfClass:[FriendshipTableViewCell class]] &&
          ![cell isMemberOfClass:[SuggestedUserTableViewCell class]]) {
        continue;
      }
      FriendshipTableViewCell* friendCell = (FriendshipTableViewCell*)cell;
      if (friendCell.user == user) {
        [friendCell.indicator stopAnimating];
        if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath]) {
          friendCell.unfollowButton.hidden = NO;
        } 
        else {
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
  if ([objectLoader.resourcePath rangeOfString:kStampedSuggestedUsersURI].location != NSNotFound) {
    self.suggestedFriends = objects;
    [self.tableView reloadData];
  }
  if ([objectLoader.resourcePath rangeOfString:@"/collections/user.json"].location != NSNotFound) {
    for (Stamp* s in objects)
      s.temporary = [NSNumber numberWithBool:NO];
  
    [Stamp.managedObjectContext save:NULL];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"Object loader %@ did fail with error %@", objectLoader, error);
  if ([objectLoader.resourcePath isEqualToString:kFriendshipCreatePath] ||
      [objectLoader.resourcePath isEqualToString:kFriendshipRemovePath]) {
    User* currentUser = [AccountManager sharedManager].currentUser;
    for (UITableViewCell* cell in tableView_.visibleCells) {
      if (![cell isMemberOfClass:[FriendshipTableViewCell class]] &&
          ![cell isMemberOfClass:[SuggestedUserTableViewCell class]]) {
        continue;
      }

      FriendshipTableViewCell* friendCell = (FriendshipTableViewCell*)cell;
      if (friendCell.indicator.isAnimating) {
        [friendCell.indicator stopAnimating];
        if ([currentUser.following containsObject:friendCell.user]) {
          [currentUser removeFollowingObject:friendCell.user];
          friendCell.followButton.hidden = NO;
          friendCell.unfollowButton.hidden = YES;
        } else {
          [currentUser addFollowingObject:friendCell.user];
          friendCell.followButton.hidden = YES;
          friendCell.unfollowButton.hidden = NO;
        }
      }
    }
  }
}

- (void)removeUsersToInviteWithIdentifers:(NSArray*)identifiers {
  self.contactsNotUsingStamped = [NSMutableArray array];

  // Fetch the address book
  ABAddressBookRef addressBook = ABAddressBookCreate();
  ABRecordRef source = ABAddressBookCopyDefaultSource(addressBook);
  CFArrayRef people = ABAddressBookCopyArrayOfAllPeopleInSourceWithSortOrdering(addressBook, source, kABPersonSortByFirstName);
  NSArray* peopleArray = [NSArray arrayWithArray:(NSArray*)people];
  for (id p in peopleArray) {
    BOOL addPerson = YES;
    ABRecordRef person = p;
    if (!person)
      continue;

    ABMultiValueRef phoneNumberProperty = ABRecordCopyValue(person, kABPersonPhoneProperty);
    NSArray* phoneNumbers = (NSArray*)ABMultiValueCopyArrayOfAllValues(phoneNumberProperty);
    CFRelease(phoneNumberProperty);
    for (NSString* identifier in identifiers) {
      if ([phoneNumbers containsObject:identifier]) {
        addPerson = NO;
        continue;
      }
    }
    [phoneNumbers release];

    ABMultiValueRef emailProperty = ABRecordCopyValue(person, kABPersonEmailProperty);
    NSArray* emails = (NSArray*)ABMultiValueCopyArrayOfAllValues(emailProperty);
    CFRelease(emailProperty);
    if (emails.count > 0) {
      for (NSString* identifier in identifiers) {
        if ([emails containsObject:identifier]) {
          addPerson = NO;
          continue;
        }
      }
    } else {
      addPerson = NO;
    }
    [emails release];
    
    if (addPerson)
      [contactsNotUsingStamped_ addObject:person];
  }
  CFRelease(addressBook);
  CFRelease(people);
  CFRelease(source);
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  self.findSource = FindFriendsSourceSuggested;
  self.stampedFriends = nil;
  [self.tableView reloadData];
  [self performSelector:@selector(resignFirstResponder)
             withObject:searchField_
             afterDelay:0.0];
  return YES;
}

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  NSString* result = [searchField_.text stringByReplacingCharactersInRange:range withString:string];
  self.findSource = result.length > 0 ? FindFriendsSourceStamped : FindFriendsSourceSuggested;
  if (findSource_ == FindFriendsSourceSuggested) {
    self.stampedFriends = nil;
    [tableView_ reloadData];
  }
  return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != searchField_)
    return YES;

  self.stampedFriends = nil;
  self.findSource = searchField_.text.length > 0 ? FindFriendsSourceStamped : FindFriendsSourceSuggested;
  [tableView_ reloadData];
  if (findSource_ == FindFriendsSourceSuggested)
    return NO;

  RKObjectManager* manager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kStampedSearchURI
                                                        delegate:self];
  loader.method = RKRequestMethodPOST;
  loader.params = [NSDictionary dictionaryWithObject:searchField_.text forKey:@"q"];
  loader.objectMapping = mapping;
  [loader send];
  [searchField_ resignFirstResponder];
  return NO;
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [searchField_ resignFirstResponder];
}

@end
