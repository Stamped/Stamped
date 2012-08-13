//
//  STFindFacebookViewController.m
//  Stamped
//
//  Created by Landon Judkins on 7/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFindFacebookViewController.h"
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
#import "STFacebook.h"
#import "STEvents.h"

typedef enum {
    STFindFacebookAuthStateNone = 0,
    STFindFacebookAuthStateReauth,
    STFindFacebookAuthStateTried,
} STFindFacebookAuthState;

static const CGFloat _batchSize = 100;

@interface STFindFacebookViewController () <UITableViewDelegate, UITableViewDataSource, STInviteTableCellDelegate>

@property (nonatomic, readwrite, retain) STCancellation* matchCancellation;
@property (nonatomic, readwrite, retain) NSMutableArray<STUserDetail>* matchUsers;

@property (nonatomic, readwrite, retain) STCancellation* friendsCancellation;

@property (nonatomic, readonly, retain) NSMutableArray* unresolvedContacts;
@property (nonatomic, readonly, retain) NSMutableSet* resolvedIDs;
@property (nonatomic, readwrite, assign) BOOL consumedAllContacts;
@property (nonatomic, readwrite, assign) NSInteger offset;

@property (nonatomic, readonly, retain) NSMutableSet* inviteIndices;

@property (nonatomic, readwrite, assign) BOOL waitingForFB;

@property (nonatomic, readwrite, assign) STFindFacebookAuthState reauthing;

@property (nonatomic, readwrite, assign) BOOL shouldShowFacebookPopUp;

@end

@implementation STFindFacebookViewController

@synthesize matchCancellation = _matchCancellation;
@synthesize matchUsers = _matchUsers;

@synthesize friendsCancellation = _friendsCancellation;

@synthesize unresolvedContacts = _unresolvedContacts;
@synthesize resolvedIDs = _resolvedIDs;
@synthesize consumedAllContacts = _consumedAllContacts;
@synthesize offset = _offset;

@synthesize inviteIndices = _inviteIndices;
@synthesize waitingForFB = _waitingForFB;

@synthesize reauthing = _reauthing;
@synthesize shouldShowFacebookPopUp = _shouldShowFacebookPopUp;

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
    [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFinished];
    [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookAuthFailed];
    [STEvents addObserver:self selector:@selector(facebookAuthChanged:) event:EventTypeFacebookLoggedOut];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(followingStatusChanged:) name:STStampedAPIFollowNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(followingStatusChanged:) name:STStampedAPIUnfollowNotification object:nil];
    if ([STFacebook sharedInstance].facebook.isSessionValid) {      
        [self loadMore];
    }
    else {
        self.waitingForFB = YES;
        [[STFacebook sharedInstance] auth];
    }
    [self reloadDataSource];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    [STEvents removeObserver:self];
    [self clearAll];
    [self updateSendButton];
}

- (void)facebookAuthChanged:(id)notImportant {
    if ([STFacebook sharedInstance].facebook.isSessionValid) {
        self.waitingForFB = NO;
        [self loadMore];
        if (self.shouldShowFacebookPopUp) {
            self.shouldShowFacebookPopUp = NO;
            [[STFacebook sharedInstance] showFacebookAlert];
        }
    }
    else if (self.reauthing == STFindFacebookAuthStateReauth) {
        self.reauthing = STFindFacebookAuthStateTried;
        [[STFacebook sharedInstance] auth];
    }
    else {
        [Util warnWithMessage:@"Could not connect to Facebook" andBlock:^{
            [Util compareAndPopController:self animated:YES];
        }];
    }
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
        message = [NSString stringWithFormat:@"Invite %@ to Stamped via Facebook?", firstName ];
    }
    else if (contacts.count == 2) {
        STContact* second = [contacts objectAtIndex:1];
        message = [NSString stringWithFormat:@"Invite %@ and %@ to Stamped via Facebook", firstName, second.name ? second.name : [second.emailAddresses objectAtIndex:0]];
    }
    else {
        message = [NSString stringWithFormat:@"Invite %@ and %d others to Stamped via Facebook", firstName, contacts.count - 1];
    }
    [Util confirmWithMessage:message action:@"Send" destructive:NO withBlock:^(BOOL success) {
        if (success) {
            Facebook* fb = [STFacebook sharedInstance].facebook;
            for (STContact* contact in contacts) {
                if (fb.isSessionValid) {
                    contact.invite = NO;
                    
                    NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                                   kFacebookAppID, @"app_id",
                                                   @"http://stamped.com", @"link",
                                                   @"Stamped", @"name", nil];
                    [params setObject:[self stampedLogoImageURL] forKey:@"picture"];
                    [params setObject:@"I think you'd like Stamped - check it out at www.stamped.com/download"
                               forKey:@"message"];
                    
                    [fb requestWithGraphPath:[contact.facebookID stringByAppendingString:@"/feed"]
                                   andParams:params
                               andHttpMethod:@"POST"
                                 andDelegate:nil];
                }
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
            self.matchCancellation = [[STStampedAPI sharedInstance] usersFromFacebookWithCallback:^(NSArray<STUserDetail> *users, NSError *error, STCancellation *cancellation) {
                [self handleMatchResponseWithUsers:users andError:error]; 
            }];
        }
        else {
            self.friendsCancellation = [STContact contactsFromFacebookWithOffset:self.offset
                                                                           limit:_batchSize
                                                                     andCallback:^(NSArray* contacts, NSError* error, STCancellation* cancellation) {
                                                                         [self handleFacebookContacts:contacts andError:error];
                                                                     }];
            self.offset += _batchSize;
        }
    }
}

- (void)clearAll {
    self.offset = 0;
    self.consumedAllContacts = NO;
    [self.friendsCancellation cancel];
    self.friendsCancellation = nil;
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
    }
    else {
        NSString* errorID = [error.userInfo objectForKey:STRestKitErrorIDKey];
        if (self.reauthing == STFindFacebookAuthStateNone && ([errorID isEqualToString:@"bad_request"] || [errorID isEqualToString:@"facebook_auth"] || [errorID isEqualToString:@"invalid_request"])) {
            if (![errorID isEqualToString:@"facebook_auth"]) {
                self.shouldShowFacebookPopUp = YES;
            }
            [self clearAll];
            self.waitingForFB = YES;
            self.reauthing = STFindFacebookAuthStateReauth;
            [[STFacebook sharedInstance] invalidate];
        }
        else {
            [Util warnWithAPIError:error andBlock:^{
                [Util compareAndPopController:self animated:YES]; 
            }];
        }
    }
    [self dataSourceDidFinishLoading];
    [self loadMore];
}

- (void)handleFacebookContacts:(NSArray*)contacts andError:(NSError*)error {
    NSInteger countBefore = self.unresolvedContacts.count;
    self.friendsCancellation = nil;
    if (contacts.count) {
        for (STContact* contact in contacts) {
            if (contact.facebookID && ![self.resolvedIDs containsObject:contact.facebookID]) {
                [self.unresolvedContacts addObject:contact];
                [self.resolvedIDs addObject:contact.facebookID];
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
    return self.matchCancellation != nil || self.friendsCancellation || self.waitingForFB;
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
        return @"Friends on Stamped";
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

- (void)followingStatusChanged:(NSNotification*)notification {
    NSString* userID = notification.object;
    for (NSInteger i = 0; i < self.matchUsers.count; i++) {
        id<STUser> user = [self.matchUsers objectAtIndex:i];
    }
}

- (NSString*)stampedLogoImageURL {
    id<STUserDetail> currentUser = [STStampedAPI sharedInstance].currentUser;
    return [NSString stringWithFormat:@"%@%@-%@%@", @"http://static.stamped.com/logos/", currentUser.primaryColor, currentUser.secondaryColor, @"-logo-195x195.png"];
}


- (void)inviteTableCellToggleInvite:(STInviteTableCell *)cell {
    NSIndexPath* path = [self.tableView indexPathForCell:cell];
    if (path) {
        
        Facebook* fb = [STFacebook sharedInstance].facebook;
        if (!fb.isSessionValid) {
            [[STFacebook sharedInstance] auth];
        }
        else {
            STContact* contact = cell.contact;
            contact.invite = !contact.invite;
            if (contact.invite) {
                [self.inviteIndices addObject:[NSNumber numberWithInteger:path.row]];
            }
            else {
                [self.inviteIndices removeObject:[NSNumber numberWithInt:path.row]];
            }
            [self updateSendButton];
        }
    }
}


@end
