//
//  STContactsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContactsViewController.h"
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

static const CGFloat _batchSize = 100;

@interface STContactsViewController () <UITableViewDelegate, UITableViewDataSource, STInviteTableCellDelegate>

@property (nonatomic, readwrite, retain) NSArray* pendingContacts;
@property (nonatomic, readwrite, retain) NSDictionary* pendingContactsByPhone;
@property (nonatomic, readwrite, retain) NSDictionary* pendingContactsByEmail;
@property (nonatomic, readwrite, retain) STCancellation* pendingPhoneCancellation;
@property (nonatomic, readwrite, retain) STCancellation* pendingEmailCancellation;
@property (nonatomic, readwrite, retain) NSArray<STUserDetail>* emailResponse;
@property (nonatomic, readwrite, retain) NSArray<STUserDetail>* phoneResponse;

@property (nonatomic, readonly, retain) NSMutableSet* resolvedUserIDs;
@property (nonatomic, readonly, retain) NSMutableArray* resolvedContacts;
@property (nonatomic, readonly, retain) NSMutableArray* unresolvedContacts;
@property (nonatomic, readwrite, assign) BOOL consumedAllContacts;
@property (nonatomic, readwrite, assign) NSInteger offset;

@property (nonatomic, readonly, retain) NSMutableSet* inviteIndices;

@end

@implementation STContactsViewController

@synthesize pendingContacts = _pendingContacts;
@synthesize pendingContactsByPhone = _pendingContactsByPhone;
@synthesize pendingContactsByEmail = _pendingContactsByEmail;
@synthesize pendingPhoneCancellation = _pendingPhoneCancellation;
@synthesize pendingEmailCancellation = _pendingEmailCancellation;
@synthesize emailResponse = _emailResponse;
@synthesize phoneResponse = _phoneResponse;

@synthesize resolvedUserIDs = _resolvedUserIDs;
@synthesize resolvedContacts = _resolvedContacts;
@synthesize unresolvedContacts = _unresolvedContacts;
@synthesize consumedAllContacts = _consumedAllContacts;
@synthesize offset = _offset;

@synthesize inviteIndices = _inviteIndices;

- (id)init
{
    self = [super init];
    if (self) {
        _resolvedContacts = [[NSMutableArray alloc] init];
        _unresolvedContacts = [[NSMutableArray alloc] init];
        _resolvedUserIDs = [[NSMutableSet alloc] init];
        _inviteIndices = [[NSMutableSet alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [self clearAll];
    [_resolvedContacts release];
    [_unresolvedContacts release];
    [_inviteIndices release];
    [_resolvedUserIDs release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    [self loadMore];
    [self reloadDataSource];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    [self clearAll];
    [self updateSendButton];
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
        message = [NSString stringWithFormat:@"Invite %@ to Stamped via email?", firstName ];
    }
    else if (contacts.count == 2) {
        STContact* second = [contacts objectAtIndex:1];
        message = [NSString stringWithFormat:@"Invite %@ and %@ to Stamped via email?", firstName, second.name ? second.name : [second.emailAddresses objectAtIndex:0]];
    }
    else {
        message = [NSString stringWithFormat:@"Invite %@ and %d others to Stamped via email?", firstName, contacts.count - 1];
    }
    [Util confirmWithMessage:message action:@"Send" destructive:NO withBlock:^(BOOL success) {
        if (success) {
            NSMutableArray* emails = [NSMutableArray array];
            for (STContact* contact in contacts) {
                contact.invite = NO;
                [emails addObject:contact.primaryEmailAddress];
            }
            NSString* emailList = [emails componentsJoinedByString:@","];
            [[STRestKitLoader sharedInstance] loadOneWithPath:@"/friendships/invite.json"
                                                         post:YES
                                                authenticated:YES
                                                       params:[NSDictionary dictionaryWithObject:emailList forKey:@"emails"]
                                                      mapping:[STSimpleBooleanResponse mapping]
                                                  andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                      
                                                  }];
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
            if (!self.pendingEmailCancellation && !self.pendingPhoneCancellation) {
                [Util executeOnMainThread:^{
                    [self dataSourceDidFinishLoading];
                }];
            }
            return;
        }
        NSInteger offset = self.offset;
        BOOL finished = YES; //just in case
        NSArray* nextPage = [STContact contactsForOffset:self.offset andLimit:_batchSize nextOffset:&offset finished:&finished];
        self.offset = offset + _batchSize;
        self.consumedAllContacts = finished;
        
        if (nextPage.count) {
            self.pendingContacts = nextPage;
            NSMutableDictionary* phoneToIndex = [NSMutableDictionary dictionary];
            NSMutableDictionary* emailToIndex = [NSMutableDictionary dictionary];
            
            for (NSInteger i = 0; i < nextPage.count; i++) {
                STContact* contact = [nextPage objectAtIndex:i];
                if (contact.phoneNumbers.count) {
                    for (NSString* phoneNumber in contact.phoneNumbers) {
                        NSMutableArray* indices = [phoneToIndex objectForKey:phoneNumber];
                        if (!indices) {
                            indices = [NSMutableArray array];
                            [phoneToIndex setObject:indices forKey:phoneNumber];
                        }
                        [indices addObject:[NSNumber numberWithInteger:i]];
                    }
                }
                if (contact.emailAddresses.count) {
                    for (NSString* email in contact.emailAddresses) {
                        NSMutableArray* indices = [emailToIndex objectForKey:email];
                        if (!indices) {
                            indices = [NSMutableArray array];
                            [emailToIndex setObject:indices forKey:email];
                        }
                        [indices addObject:[NSNumber numberWithInteger:i]];
                    }
                }
            }
            
            self.pendingContactsByEmail = emailToIndex;
            self.pendingContactsByPhone = phoneToIndex;
            
            NSAssert1( phoneToIndex.count + emailToIndex.count > 0, @"page should have at least one entry for page %@", nextPage);
            if (phoneToIndex.count) {
                self.pendingPhoneCancellation = [[STStampedAPI sharedInstance] usersWithPhoneNumbers:phoneToIndex.allKeys
                                                                                         andCallback:^(NSArray<STUserDetail> *users, NSError *error, STCancellation *cancellation) {
                                                                                             [self handlePhoneResponseWithUsers:users andError:error];
                                                                                         }];
            }
            if (emailToIndex.count) {
                self.pendingEmailCancellation = [[STStampedAPI sharedInstance] usersWithEmails:emailToIndex.allKeys
                                                                                   andCallback:^(NSArray<STUserDetail> *users, NSError *error, STCancellation *cancellation) {
                                                                                       [self handleEmailResponseWithUsers:users andError:error]; 
                                                                                   }];
            }
        }
    }
}

- (void)clearAll {
    self.offset = 0;
    self.consumedAllContacts = NO;
    [self.resolvedContacts removeAllObjects];
    [self.unresolvedContacts removeAllObjects];
    [self.resolvedUserIDs removeAllObjects];
    [self.inviteIndices removeAllObjects];
    self.pendingContacts = nil;
    self.pendingContactsByEmail = nil;
    self.pendingContactsByPhone = nil;
    [self.pendingEmailCancellation cancel];
    [self.pendingPhoneCancellation cancel];
    self.pendingEmailCancellation = nil;
    self.pendingPhoneCancellation = nil;
    self.emailResponse = nil;
    self.phoneResponse = nil;
}

- (void)handleEmailResponseWithUsers:(NSArray<STUserDetail>*)users andError:(NSError*)error {
    self.pendingEmailCancellation = nil;
    self.emailResponse = users;
    [self handleBoth];
}

- (void)handlePhoneResponseWithUsers:(NSArray<STUserDetail>*)users andError:(NSError*)error {
    self.pendingPhoneCancellation = nil;
    self.phoneResponse = users;
    [self handleBoth];
}

- (void)handleBoth {
    if (!self.pendingPhoneCancellation && !self.pendingEmailCancellation) {
        if (self.phoneResponse.count) {
            for (id<STUserDetail> user in self.phoneResponse) {
                NSString* searchID = [user searchIdentifier];
                NSArray* indices = [self.pendingContactsByPhone objectForKey:searchID];
                if (indices.count) {
                    for (NSNumber* index in indices) {
                        STContact* contact = [self.pendingContacts objectAtIndex:index.integerValue];
                        contact.userDetail = user;
                    }
                }
            }
        }
        if (self.emailResponse.count) {
            for (id<STUserDetail> user in self.emailResponse) {
                NSString* searchID = [user searchIdentifier];
                NSArray* indices = [self.pendingContactsByEmail objectForKey:searchID];
                if (indices.count) {
                    for (NSNumber* index in indices) {
                        STContact* contact = [self.pendingContacts objectAtIndex:index.integerValue];
                        contact.userDetail = user;
                    }
                }
            }
        }
        NSInteger countBefore = self.resolvedContacts.count;
        for (STContact* contact in self.pendingContacts) {
            if (contact.userDetail) {
                NSString* userID = contact.userDetail.userID;
                if (![self.resolvedUserIDs containsObject:userID]) {
                    [self.resolvedContacts addObject:contact];
                    [self.resolvedUserIDs addObject:userID];
                }
            }
            else if (contact.emailAddresses.count) {
                [self.unresolvedContacts addObject:contact];
            }
        }
        NSInteger delta = self.resolvedContacts.count - countBefore;
        self.pendingContacts = nil;
        self.emailResponse = nil;
        self.phoneResponse = nil;
        self.pendingContactsByEmail = nil;
        self.pendingContactsByPhone = nil;
        [self dataSourceDidFinishLoading];
        if (delta || self.consumedAllContacts) {
            [self.tableView beginUpdates];
            if (delta) {
                
                NSMutableArray* indices = [NSMutableArray array];
                for (NSInteger i = 0; i < delta; i++) {
                    [indices addObject:[NSIndexPath indexPathForRow:countBefore + i inSection:0]];
                }
                [self.tableView insertRowsAtIndexPaths:indices withRowAnimation:UITableViewRowAnimationNone];
            }
            if (self.consumedAllContacts) {
                [self.tableView insertSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationNone];
            }
            [self.tableView endUpdates];
        }
        [self loadMore]; 
    }
}

#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return self.pendingEmailCancellation || self.pendingPhoneCancellation;
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
    return self.resolvedContacts.count + self.unresolvedContacts.count == 0 && self.consumedAllContacts;
}

- (void)noDataTapped:(id)notImportant {
    [Util compareAndPopController:self animated:YES];
}

- (void)setupNoDataView:(NoDataView*)view {
    [view setupWithTitle:@"No contacts" detailTitle:@"Click here to go back."];
}

#pragma mark - TableView methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    if (self.consumedAllContacts && self.unresolvedContacts.count) {
        return 2;
    }
    return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) {
        return self.resolvedContacts.count;
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
        
        STContact* contact = [self.resolvedContacts objectAtIndex:indexPath.row];
        id<STUserDetail> user = contact.userDetail;
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
    STContact* contact = [self.resolvedContacts objectAtIndex:indexPath.row]; 
    id<STUserDetail> user = contact.userDetail;
    if (contact) {
        STActionContext* context = [STActionContext context];
        context.user = user;
        id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
}

- (void)friendTableCellToggleFollowing:(FriendTableCell*)cell {
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    if (indexPath) {
        STContact* contact = [self.resolvedContacts objectAtIndex:indexPath.row]; 
        if (contact.userDetail.following.boolValue) {
            [[STStampedAPI sharedInstance] removeFriendForUserID:contact.userDetail.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
                if (userDetail) {
                    contact.userDetail = userDetail;
                    [self.tableView reloadData];
                }
            }];
        }
        else {
            [[STStampedAPI sharedInstance] addFriendForUserID:contact.userDetail.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
                if (userDetail) {
                    contact.userDetail = userDetail;
                    [self.tableView reloadData];
                }
            }];
        }
    }
}

- (void)inviteTableCellToggleInvite:(STInviteTableCell *)cell {
    NSIndexPath* path = [self.tableView indexPathForCell:cell];
    if (path) {
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

@end
