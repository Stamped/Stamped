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
#import "STEvents.h"

#define kUserLimit 20

@interface Friends (Internal)
- (NSArray*)emailAddresses;
@end

@implementation Friends
@synthesize requestType=_requestType;
@synthesize reloading=_reloading;
@synthesize moreData=_moreData;
@synthesize requestParameters;
@synthesize query = _query;

- (id)init {
    if ((self = [super init])) {
        _data = [[NSArray alloc] init];
    }
    return self;
}

- (void)dealloc {
    
    if (_cancellation) {
        [_cancellation cancel];
        [_cancellation release];
        _cancellation = nil;
    }
    
    self.requestParameters=nil;
    [_data release], _data=nil;
    [_query release];
    [super dealloc];
}


#pragma mark Loading

- (void)loadWithPath:(NSString*)path params:(NSDictionary*)params {
            
    _cancellation = [[[STRestKitLoader sharedInstance] loadWithPath:path 
                                                               post:(params!=nil) 
                                                         authPolicy:STRestKitAuthPolicyOptional 
                                                             params:(params==nil) ? [NSDictionary dictionary] : params mapping:[STSimpleUser mapping]
                                                        andCallback:^(NSArray *users, NSError *error, STCancellation *cancellation) {

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
        case FriendsRequestTypeTwitter:
            return @"/users/find/twitter.json";
        case FriendsRequestTypeFacebook:
            return @"/users/find/facebook.json";
        case FriendsRequestTypeSuggested:
            return @"/users/suggested.json";
        case FriendsRequestTypeSearch:
            return @"/users/search.json";
        default:
            break;
    }
    return nil;
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
            addresses = [addresses stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
            self.requestParameters = [NSDictionary dictionaryWithObject:addresses forKey:@"query"];
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

- (void)setQuery:(NSString *)query {
    _requestType = FriendsRequestTypeSearch;
    [_query release];
    _query = [query copy];
    self.requestParameters = [NSDictionary dictionaryWithObject:query forKey:@"query"];
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
