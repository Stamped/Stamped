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

static const CGFloat _batchSize = 100;

@interface STContactsViewController ()

@property (nonatomic, readwrite, retain) NSArray* pendingContacts;
@property (nonatomic, readwrite, retain) NSDictionary* pendingContactsByPhone;
@property (nonatomic, readwrite, retain) NSDictionary* pendingContactsByEmail;
@property (nonatomic, readwrite, retain) STCancellation* pendingPhoneCancellation;
@property (nonatomic, readwrite, retain) STCancellation* pendingEmailCancellation;
@property (nonatomic, readwrite, retain) NSArray* emailResponse;
@property (nonatomic, readwrite, retain) NSArray* phoneResponse;

@property (nonatomic, readonly, retain) NSMutableArray* resolvedContacts;
@property (nonatomic, readonly, retain) NSMutableArray* unresolvedContacts;
@property (nonatomic, readwrite, assign) BOOL consumedAllContacts;
@property (nonatomic, readwrite, assign) NSInteger offset;

@end

@implementation STContactsViewController

@synthesize pendingContacts = _pendingContacts;
@synthesize pendingContactsByPhone = _pendingContactsByPhone;
@synthesize pendingContactsByEmail = _pendingContactsByEmail;
@synthesize pendingPhoneCancellation = _pendingPhoneCancellation;
@synthesize pendingEmailCancellation = _pendingEmailCancellation;
@synthesize emailResponse = _emailResponse;
@synthesize phoneResponse = _phoneResponse;

@synthesize resolvedContacts = _resolvedContacts;
@synthesize unresolvedContacts = _unresolvedContacts;
@synthesize offset = _offset;

- (id)init
{
    self = [super init];
    if (self) {
        _resolvedContacts = [[NSMutableArray alloc] init];
        _unresolvedContacts = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [self clearAll];
    [_resolvedContacts release];
    [_unresolvedContacts release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (void)loadMore {
    if (!self.consumedAllContacts && ![self dataSourceReloading]) {
        NSInteger offset = self.offset;
        BOOL finished = YES; //just in case
        NSArray* nextPage = [STContact contactsForOffset:self.offset andLimit:_batchSize nextOffset:&offset finished:&finished];
        self.offset = offset;
        self.consumedAllContacts = finished;
        
        if (nextPage.count) {
            self.pendingContacts = nextPage;
            NSMutableDictionary* phoneToIndex = [NSMutableDictionary dictionary];
            NSMutableDictionary* emailToIndex = [NSMutableDictionary dictionary];
            
            for (NSInteger i = 0; i < nextPage.count; i++) {
                STContact* contact = [nextPage objectAtIndex:i];
                if (contact.phoneNumbers) {
                    for (NSString* phoneNumber in contact.phoneNumbers) {
                        NSMutableArray* indices = [phoneToIndex objectForKey:phoneNumber];
                        if (!indices) {
                            indices = [NSMutableArray array];
                            [phoneToIndex setObject:indices forKey:phoneNumber];
                        }
                        [indices addObject:[NSNumber numberWithInteger:i]];
                    }
                }
                if (contact.emailAddresses) {
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
            
            NSAssert1( phoneToIndex.count + emailToIndex.count > 0, @"page should have at least one entry for page %@", nextPage);
            if (phoneToIndex.count) {
                
            }
        }
    }
}

- (void)clearAll {
    self.offset = 0;
    self.consumedAllContacts = NO;
    [self.resolvedContacts removeAllObjects];
    [self.unresolvedContacts removeAllObjects];
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
    [self clearAll];
    [self.tableView reloadData];
    [super reloadDataSource];
}

- (void)dataSourceDidFinishLoading {
    [super dataSourceDidFinishLoading];
}

- (BOOL)dataSourceIsEmpty {
    return self.resolvedContacts.count + self.unresolvedContacts.count == 0;
}

- (void)noDataTapped:(id)notImportant {
    //[Util warnWithMessage:@"not implemented yet..." andBlock:nil];
}

- (void)setupNoDataView:(NoDataView*)view {
    [view setupWithTitle:@"No contacts" detailTitle:@"No contact information was available"];
}


@end
