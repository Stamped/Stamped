//
//  STFindTwitterViewController.m
//  Stamped
//
//  Created by Landon Judkins on 7/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFindTwitterViewController.h"
#import "STContact.h"
#import "STCancellation.h"
#import "Util.h"
#import "STDebug.h"
#import "FriendTableCell.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STInviteTableCell.h"
#import "STRestKitLoader.h"
#import "STSimpleBooleanResponse.h"
#import "STTwitter.h"
#import "STEvents.h"
#import "TwitterAccountsViewController.h"

typedef enum {
    _authStateNone = 0,
    _authStateReauth,
    _authStateTried,
} _authState;

static const CGFloat _batchSize = 100;

@interface STFindTwitterViewController () <UITableViewDelegate, UITableViewDataSource, STInviteTableCellDelegate>

@property (nonatomic, readwrite, retain) STCancellation* matchCancellation;
@property (nonatomic, readwrite, retain) NSMutableArray<STUserDetail>* matchUsers;

@property (nonatomic, readwrite, retain) STCancellation* friendsCancellation;

@property (nonatomic, readonly, retain) NSMutableArray* unresolvedContacts;
@property (nonatomic, readonly, retain) NSMutableSet* resolvedIDs;
@property (nonatomic, readwrite, assign) BOOL consumedAllContacts;
@property (nonatomic, readwrite, assign) NSInteger offset;

@property (nonatomic, readonly, retain) NSMutableSet* inviteIndices;

@property (nonatomic, readwrite, assign) BOOL waitingForTwitter;

@property (nonatomic, readwrite, assign) _authState authState;

@end

@implementation STFindTwitterViewController

@synthesize matchCancellation = _matchCancellation;
@synthesize matchUsers = _matchUsers;

@synthesize friendsCancellation = _friendsCancellation;

@synthesize unresolvedContacts = _unresolvedContacts;
@synthesize resolvedIDs = _resolvedIDs;
@synthesize consumedAllContacts = _consumedAllContacts;
@synthesize offset = _offset;

@synthesize inviteIndices = _inviteIndices;
@synthesize waitingForTwitter = _waitingForTwitter;

@synthesize authState = _authState;

- (id)init
{
    self = [super init];
    if (self) {
        _unresolvedContacts = [[NSMutableArray alloc] init];
        _resolvedIDs = [[NSMutableSet alloc] init];
        _inviteIndices = [[NSMutableSet alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [self clearAll];
    [_unresolvedContacts release];
    [_resolvedIDs release];
    [_inviteIndices release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    [STEvents addObserver:self selector:@selector(twitterAuthChanged:) event:EventTypeTwitterAuthFailed];
    [STEvents addObserver:self selector:@selector(twitterAuthChanged:) event:EventTypeTwitterAuthFinished];
    if ([[STTwitter sharedInstance] isSessionValid]) {        
        [self loadMore];
    }
    else {
        self.waitingForTwitter = YES;
        [[STTwitter sharedInstance] auth];
    }
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    [STEvents removeObserver:self];
    [self clearAll];
    [self updateSendButton];
}

- (void)twitterAuthChanged:(id)notImportant {
    if ([STTwitter sharedInstance].isSessionValid) {
        
        NSMutableDictionary* params = [NSMutableDictionary dictionary];
        STTwitter* twitter = [STTwitter sharedInstance];
        [params setObject:twitter.twitterUsername forKey:@"linked_screen_name"];
        [params setObject:twitter.twitterToken forKey:@"token"];
        [params setObject:twitter.twitterTokenSecret forKey:@"secret"];
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/twitter/add.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  if (result) {
                                                      self.waitingForTwitter = NO;
                                                      [self loadMore];
                                                  }
                                                  else {
                                                      [Util warnWithAPIError:error andBlock:^{
                                                          [Util compareAndPopController:self animated:YES];
                                                      }];
                                                  }
                                              }];
    }
    else {
        [Util warnWithMessage:@"Could not connect to Twitter" andBlock:^{
            [Util compareAndPopController:self animated:YES];
        }];
    }
}

- (void)sendTweet:(NSString*)tweet {
    [[STTwitter sharedInstance] sendTweet:tweet withCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        
    }];
}

- (void)sendButtonClicked:(id)notImportant {
    NSString* message;
    NSMutableArray* contacts = [NSMutableArray array];
    for (NSNumber* index in self.inviteIndices) {
        STContact* contact = [self.unresolvedContacts objectAtIndex:index.integerValue];
        [contacts addObject:contact];
    }
    NSAssert1(contacts.count > 0, @"contacts should not be empty:%@", self.inviteIndices);
    if (contacts.count == 0) return;
    STContact* first = [contacts objectAtIndex:0];
    NSString* firstName = first.name ? first.name : [first.emailAddresses objectAtIndex:0];
    if (contacts.count == 1) {
        message = [NSString stringWithFormat:@"Invite %@ to Stamped via Twitter?", firstName ];
    }
    else if (contacts.count == 2) {
        STContact* second = [contacts objectAtIndex:1];
        message = [NSString stringWithFormat:@"Invite %@ and %@ to Stamped via Twitter", firstName, second.name ? second.name : [second.emailAddresses objectAtIndex:0]];
    }
    else {
        message = [NSString stringWithFormat:@"Invite %@ and %d others to Stamped via Twitter", firstName, contacts.count - 1];
    }
    [Util confirmWithMessage:message action:@"Send" destructive:NO withBlock:^(BOOL success) {
        if (success) {
            for (STContact* contact in contacts) {
                [self sendTweet:[NSString stringWithFormat:@"@%@ I’m using @stampedapp to record and share my favorite things. Join me! www.stamped.com", contact.twitterUsername]];
            }
            [self.inviteIndices removeAllObjects];
            [self updateSendButton];
        }
    }];
}

- (void)updateSendButton {
    UIBarButtonItem* item = nil;
    if (self.inviteIndices.count) {
        item = [[[UIBarButtonItem alloc] initWithTitle:[NSString stringWithFormat:@"Send (%d)", self.inviteIndices.count]
                                                 style:UIBarButtonItemStyleDone
                                                target:self 
                                                action:@selector(sendButtonClicked:)] autorelease];
    }
    self.navigationItem.rightBarButtonItem = item;
}

- (void)loadMore {
    if (![self dataSourceReloading] && !self.consumedAllContacts) {
        if (self.consumedAllContacts) {
            if (![self dataSourceReloading]) {
                [Util executeOnMainThread:^{
                    [self dataSourceDidFinishLoading];
                }];
            }
            return;
        }
        
        if (!self.matchUsers) {
            self.matchCancellation = [[STStampedAPI sharedInstance] usersFromTwitterWithCallback:^(NSArray<STUserDetail> *users, NSError *error, STCancellation *cancellation) {
                [self handleMatchResponseWithUsers:users andError:error]; 
            }];
        }
        else {
            self.friendsCancellation = [STContact contactsFromTwitterWithOffset:self.offset
                                                                          limit:_batchSize
                                                                    andCallback:^(NSArray* contacts, NSError* error, STCancellation* cancellation) {
                                                                        [self handleTwitterContacts:contacts andError:error];
                                                                    }];
            self.offset += _batchSize;
        }
    }
}

- (void)clearAll {
    self.offset = 0;
    self.consumedAllContacts = NO;
    [self.unresolvedContacts removeAllObjects];
    [self.inviteIndices removeAllObjects];
    [self.matchCancellation cancel];
    self.matchCancellation = nil;
    self.matchUsers = nil;
}

- (void)handleMatchResponseWithUsers:(NSArray<STUserDetail>*)users andError:(NSError*)error {
    if (users) {
        self.matchUsers = [NSMutableArray arrayWithArray:users];
        for (id<STUserDetail> user in self.matchUsers) {
            if (user.searchIdentifier) {
                [self.resolvedIDs addObject:user.searchIdentifier];
            }
        }
        self.matchCancellation = nil;
        [self.tableView beginUpdates];
        [self.tableView insertSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationNone];
        [self.tableView endUpdates];
        [self dataSourceDidFinishLoading];
        [self loadMore];
    }
    else {
        NSString* errorID = [error.userInfo objectForKey:STRestKitErrorIDKey];
        if (self.authState == _authStateNone && ([errorID isEqualToString:@"bad_request"] || [errorID isEqualToString:@"invalid_request"])) {
            self.waitingForTwitter = YES;
            self.authState = _authStateReauth;
            [self twitterAuthChanged:nil];
            [self dataSourceDidFinishLoading];
        }
        else {
            self.consumedAllContacts = YES;
            [Util warnWithAPIError:error andBlock:^{
                [Util compareAndPopController:self animated:YES]; 
            }];
        }
    }
}

- (void)handleTwitterContacts:(NSArray*)contacts andError:(NSError*)error {
    NSInteger countBefore = self.unresolvedContacts.count;
    self.friendsCancellation = nil;
    if (contacts.count) {
        for (STContact* contact in contacts) {
            if (contact.twitterID && contact.twitterUsername && ![self.resolvedIDs containsObject:contact.twitterID]) {
                [self.unresolvedContacts addObject:contact];
                [self.resolvedIDs addObject:contact.twitterID];
            }
        }
        NSInteger delta = self.unresolvedContacts.count - countBefore;
        if (delta) {
            [self.tableView beginUpdates];
            if (countBefore == 0) {
                [self.tableView insertSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationNone];
            }
            else {
                NSMutableArray* rows = [NSMutableArray array];
                for (NSInteger i = 0; i < delta; i++) {
                    [rows addObject:[NSIndexPath indexPathForRow:countBefore + i inSection:1]];
                }
                [self.tableView insertRowsAtIndexPaths:rows withRowAnimation:UITableViewRowAnimationNone];
            }
            [self.tableView endUpdates];
        }
    }
    else {
        self.consumedAllContacts = YES;
        if (error) {
            [Util warnWithAPIError:error andBlock:nil];
        }
    }
    [self dataSourceDidFinishLoading];
}

#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return self.matchCancellation != nil || self.friendsCancellation || self.waitingForTwitter;
} 

- (void)loadNextPage {
    [self loadMore];
}


- (BOOL)dataSourceHasMoreData {
    return !self.consumedAllContacts || [self dataSourceReloading];
}

- (void)reloadDataSource {
    [self loadMore];
    [super reloadDataSource];
}

- (void)dataSourceDidFinishLoading {
    [super dataSourceDidFinishLoading];
}

- (BOOL)dataSourceIsEmpty {
    return self.matchUsers.count && self.unresolvedContacts.count == 0 && self.consumedAllContacts;
}

- (void)noDataTapped:(id)notImportant {
    [Util compareAndPopController:self animated:YES];
}

- (void)setupNoDataView:(NoDataView*)view {
    [view setupWithTitle:@"No friends available" detailTitle:@"Click here to go back."];
}

#pragma mark - TableView methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    if (self.unresolvedContacts.count) {
        return 2;
    }
    else if (self.matchUsers) {
        return 1;
    }
    return 0;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) {
        return self.matchUsers.count;
    }
    else {
        return self.unresolvedContacts.count;
    }
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 0) {
        static NSString *CellIdentifier = @"CellIdentifier";
        FriendTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            cell = [[FriendTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier];
            cell.delegate = (id<FriendTableCellDelegate>)self;
        }
        
        id<STUserDetail> user = [self.matchUsers objectAtIndex:indexPath.row];
        
        [cell setupWithUser:user];
        
        return cell;
    }
    else {
        static NSString *CellIdentifier2 = @"CellIdentifier2";
        STInviteTableCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier2];
        if (cell == nil) {
            cell = [[[STInviteTableCell alloc] initWithReuseIdentifier:CellIdentifier2] autorelease];
        }
        cell.delegate = self;
        STContact* contact = [self.unresolvedContacts objectAtIndex:indexPath.row];
        [cell setupWithContact:contact];
        
        return cell;
    }
}

- (NSString*)tableView:(UITableView*)tableView titleForHeaderInSection:(NSInteger)section {
    if (section == 0) {
        return @"Friends from Stamped";
    }
    else {
        return @"Invite Friends to Stamped";
    }
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (![self tableView:tableView titleForHeaderInSection:section]) {
        return 0.0f;
    }
    return 25.0f;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 64.0f;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    NSString *title = [self tableView:tableView titleForHeaderInSection:section];
    if (title) {
        
        UIImage *image = [UIImage imageNamed:@"find_friends_section_header_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, image.size.height)];
        imageView.image = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(10.0f, floorf((imageView.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.font = font;
        label.textColor = [UIColor whiteColor];
        label.backgroundColor = [UIColor clearColor];
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.2f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.text =  title;
        [imageView addSubview:label];
        [label sizeToFit];
        [label release];
        
        return [imageView autorelease];
        
    }
    
    return nil;
    
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section != 0) return;
    id<STUserDetail> user = [self.matchUsers objectAtIndex:indexPath.row];
    if (user) {
        STActionContext* context = [STActionContext context];
        context.user = user;
        id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
}

- (void)friendTableCellToggleFollowing:(FriendTableCell*)cell {
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    if (indexPath) {
        id<STUserDetail> userDetail = [self.matchUsers objectAtIndex:indexPath.row];
        if (userDetail.following.boolValue) {
            [[STStampedAPI sharedInstance] removeFriendForUserID:userDetail.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
                if (userDetail) {
                    [self.matchUsers replaceObjectAtIndex:indexPath.row withObject:userDetail];
                    [self.tableView reloadData];
                }
            }];
        }
        else {
            [[STStampedAPI sharedInstance] addFriendForUserID:userDetail.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
                if (userDetail) {
                    [self.matchUsers replaceObjectAtIndex:indexPath.row withObject:userDetail];
                    [self.tableView reloadData];
                }
            }];
        }
    }
}

- (NSString*)stampedLogoImageURL {
    id<STUserDetail> currentUser = [STStampedAPI sharedInstance].currentUser;
    return [NSString stringWithFormat:@"%@%@-%@%@", @"http://static.stamped.com/logos/", currentUser.primaryColor, currentUser.secondaryColor, @"-logo-195x195.png"];
}


- (void)inviteTableCellToggleInvite:(STInviteTableCell *)cell {
    NSIndexPath* path = [self.tableView indexPathForCell:cell];
    if (path) {
        
        //        Facebook* fb = [STFacebook sharedInstance].facebook;
        //        if (!fb.isSessionValid) {
        //            [[STFacebook sharedInstance] auth];
        //        }
        //        else {
        STContact* contact = cell.contact;
        contact.invite = !contact.invite;
        if (contact.invite) {
            [self.inviteIndices addObject:[NSNumber numberWithInteger:path.row]];
        }
        else {
            [self.inviteIndices removeObject:[NSNumber numberWithInt:path.row]];
        }
        [self updateSendButton];
        //        }
    }
}


@end
