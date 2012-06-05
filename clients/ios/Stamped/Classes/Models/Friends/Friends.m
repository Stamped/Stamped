//
//  Friends.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "Friends.h"
#import <AddressBook/AddressBook.h>
#import "STStampedAPI.h"
#import "STSimpleUser.h"
#import "STRestKitLoader.h"
#import "STFacebook.h"
#import "STTwitter.h"

#define kUserLimit 20

@interface Friends (Internal)
- (NSArray*)emailAddresses;
@end

@implementation Friends
@synthesize requestType=_requestType;
@synthesize reloading=_reloading;
@synthesize moreData=_moreData;
@synthesize requestParameters;

/*
 'v0/users/suggested.json'
 'v0/users/find/email.json
 'v0/users/find/phone.json
 'v0/users/find/twitter.json
 'v0/users/find/facebook.json
 
 Find email and find phone take one arg a comma separated list of phone numbers or email addresses: 
 
 q, basestring
 
 find/twitter.json:
 
 user_token, basestring
 user_secret, basestring
 
 find/facebook.json:
 
 user_token, basestring
 */

- (id)init {
    if ((self = [super init])) {
        _data = [[NSArray alloc] init];
    }
    return self;
}

- (void)dealloc {
    
    if (_cancellation) {
        [_cancellation cancel];
        _cancellation = nil;
    }
    
    self.requestParameters=nil;
    [_data release], _data=nil;
    [super dealloc];
}


#pragma mark Loading

- (void)loadWithPath:(NSString*)path params:(NSDictionary*)params {
    
    NSLog(@"%@", params);
            
    _cancellation = [[[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleUser mapping] andCallback:^(NSArray *users, NSError *error, STCancellation *cancellation) {

        _moreData = NO;
        if (users) {
            
            _moreData = ([users count] == kUserLimit);            
            NSMutableArray *array = [_data mutableCopy];
            NSMutableArray *identifiers = [_identifiers mutableCopy];
            
            for (id<STUser> user in users) {
                if (![identifiers containsObject:user.userID]) {
                    [array addObject:user];
                    [identifiers addObject:user.userID];
                }
            }
            
            [_data release], _data = nil;
            [_identifiers release], _identifiers = nil;
            
            _data = [array retain];
            _identifiers = [identifiers retain];
            [_cancellation release], _cancellation=nil;
            
            [array release];
            [identifiers release];
                        
        }
        
        [_cancellation release], _cancellation=nil;
        _reloading = NO;
        [STEvents postEvent:EventTypeFriendsFinished identifier:[NSString stringWithFormat:@"friends-%i", _requestType] object:nil];
        
    }] retain];
    
    
}

- (NSString*)path {
    
    switch (_requestType) {
        case FriendsRequestTypeContacts:
            return @"/users/find/email.json";
            break;
        case FriendsRequestTypeTwitter:
            return @"/users/find/twitter.json";
            break;
        case FriendsRequestTypeFacebook:
            return @"/users/find/facebook.json";
            break;
        case FriendsRequestTypeSuggested:
            return @"/users/suggested.json";
            break;
        default:
            break;
    }
    
}

- (void)reloadData {
    if (_reloading) return;
    _reloading = YES;
    [self loadWithPath:[self path] params:self.requestParameters];
}

- (void)loadNextPage {
    if (_reloading) return;
    _reloading = YES;

    
    NSLog(@"loading nex page : %@", _moreData ? @"YES" : @"NO");
    
    
}


#pragma mark - Setters

- (void)setRequestType:(FriendsRequestType)requestType {
    _requestType = requestType;
    
    switch (_requestType) {
        case FriendsRequestTypeContacts:{
            NSString *addresses = [[self emailAddresses] componentsJoinedByString:@","];
            self.requestParameters = [NSDictionary dictionaryWithObject:addresses forKey:@"q"];
        }
            break;
        case FriendsRequestTypeTwitter:
            if ([[STTwitter sharedInstance] isSessionValid]) {
                NSString *token = [[STTwitter sharedInstance] twitterToken];
                NSString *tokenSecret = [[STTwitter sharedInstance] twitterTokenSecret];
                self.requestParameters = [NSDictionary dictionaryWithObjectsAndKeys:token, @"user_token", tokenSecret, @"user_secret", nil];
            }
            break;
        case FriendsRequestTypeFacebook:
            if ([[STFacebook sharedInstance] isSessionValid]) {
                NSString *token = [[[STFacebook sharedInstance] facebook] accessToken];
                self.requestParameters = [NSDictionary dictionaryWithObject:token forKey:@"user_token"];
            }
            break;
        default:
            break;
    }
    
    
    
}


#pragma mark - AddressBook Getter

- (NSArray*)emailAddresses {
    
    ABAddressBookRef addressBook = ABAddressBookCreate();
    CFArrayRef people = ABAddressBookCopyArrayOfAllPeople(addressBook);
    NSMutableArray *allEmails = [[NSMutableArray alloc] initWithCapacity:CFArrayGetCount(people)];
    for (CFIndex i = 0; i < CFArrayGetCount(people); i++) {
        ABRecordRef person = CFArrayGetValueAtIndex(people, i);
        ABMultiValueRef emails = ABRecordCopyValue(person, kABPersonEmailProperty);
        for (CFIndex j=0; j < ABMultiValueGetCount(emails); j++) {
            CFTypeRef email = ABMultiValueCopyValueAtIndex(emails, j);
            [allEmails addObject:(NSString*)email];
            CFRelease(email);
        }
        CFRelease(emails);
    }
    CFRelease(addressBook);
    CFRelease(people);

    return [allEmails autorelease];
    
}


#pragma mark - Friend Actions

- (void)follow {
    
    
    
}

- (void)invite {
    
    
    
}


#pragma mark - DataSource

- (NSInteger)numberOfObjects {
    return [_data count];
}

- (id)objectAtIndex:(NSInteger)index {
    if (index < 0 || index >= [_data count]) return nil;
    return [_data objectAtIndex:index];
}

- (BOOL)isEmpty {
    return [_data count] == 0;
}


@end
