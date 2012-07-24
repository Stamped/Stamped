//
//  STContact.m
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContact.h"
#import <AddressBook/AddressBook.h>
#import "Util.h"

@implementation STContact

@synthesize name = _name;
@synthesize phoneNumbers = _phoneNumbers;
@synthesize emailAddresses = _emailAddresses;
@synthesize invite = _invite;
@synthesize image = _image;
@synthesize imageURL = _imageURL;
@synthesize facebookID = _facebookID;
@synthesize twitterUsername = _twitterUsername;
@synthesize twitterID = _twitterID;

@synthesize userDetail = _userDetail;

- (void)dealloc
{
    [_name release];
    [_phoneNumbers release];
    [_emailAddresses release];
    [_userDetail release];
    [_image release];
    [_imageURL release];
    [_facebookID release];
    [_twitterUsername release];
    [_twitterID release];
    [super dealloc];
}

- (NSString *)primaryEmailAddress {
    if (self.emailAddresses.count) {
        return [self.emailAddresses objectAtIndex:0];
    }
    else {
        return nil;
    }
}

+ (NSArray*)contactsForOffset:(NSInteger)offset andLimit:(NSInteger)limit nextOffset:(NSInteger*)nextOffset finished:(BOOL*)finished {
    NSMutableArray* contacts = [NSMutableArray array];
    ABAddressBookRef addressBook = ABAddressBookCreate();
    CFArrayRef people = ABAddressBookCopyArrayOfAllPeople(addressBook);
    CFMutableArrayRef peopleMutable = CFArrayCreateMutableCopy(
                                                               kCFAllocatorDefault,
                                                               CFArrayGetCount(people),
                                                               people
                                                               );
    
    
    CFArraySortValues(
                      peopleMutable,
                      CFRangeMake(0, CFArrayGetCount(peopleMutable)),
                      (CFComparatorFunction) ABPersonComparePeopleByName,
                      (void*) ABPersonGetSortOrdering()
                      );
    CFIndex numPeople = ABAddressBookGetPersonCount(addressBook);
    NSInteger i = offset;
    while (contacts.count < limit && i < numPeople) {
        
        ABRecordRef person = CFArrayGetValueAtIndex(peopleMutable, i);
        STContact* contact = [[[STContact alloc] init] autorelease];
        
        CFStringRef nameRef = ABRecordCopyCompositeName(person);
        if (nameRef) {
            contact.name = (NSString*)nameRef;
            CFRelease(nameRef);
        }
        if (ABPersonHasImageData(person)) {
            CFDataRef dataRef = ABPersonCopyImageDataWithFormat(person, kABPersonImageFormatThumbnail);
            if (dataRef) {
                contact.image = [UIImage imageWithData:(NSData*)dataRef];
                CFRelease(dataRef);
            }
        }
        
        ABMultiValueRef phoneNumberProperty = ABRecordCopyValue(person, kABPersonPhoneProperty);
        if (phoneNumberProperty) {
            NSArray* phoneNumbers = (NSArray*)ABMultiValueCopyArrayOfAllValues(phoneNumberProperty);
            if (phoneNumbers) {
                NSMutableArray* sanitizedNumbers = [NSMutableArray array];
                for (NSString* num in phoneNumbers) {
                    NSString* sanitized = [Util sanitizedPhoneNumberFromString:num];
                    if (sanitized) {
                        [sanitizedNumbers addObject:sanitized];
                    }
                }
                contact.phoneNumbers = sanitizedNumbers;
                [phoneNumbers release];
            }
            CFRelease(phoneNumberProperty);
        }
        
        ABMultiValueRef emailProperty = ABRecordCopyValue(person, kABPersonEmailProperty);
        if (emailProperty) {
            NSArray* emails = (NSArray*)ABMultiValueCopyArrayOfAllValues(emailProperty);
            if (emails) {
                contact.emailAddresses = emails;
                [emails release];
            }
            CFRelease(emailProperty);
        }
        if (contact.name.length && (contact.phoneNumbers.count || contact.emailAddresses.count)) {
            [contacts addObject:contact];
        }
        i++;
    }
    *finished = i == numPeople;
    
    CFRelease(addressBook);
    CFRelease(people);
    CFRelease(peopleMutable);
    return contacts;
}

+ (RKObjectMapping*)facebookMapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPathsToAttributes:
     @"image_url", @"imageURL",
     @"name", @"name",
     @"user_id", @"facebookID",
     nil];
    
    return mapping;
}

+ (RKObjectMapping*)twitterMapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPathsToAttributes:
     @"image_url", @"imageURL",
     @"name", @"name",
     @"screen_name", @"twitterUsername",
     @"user_id", @"twitterID",
     nil];
    
    return mapping;
}

+ (STCancellation*)contactsFromFacebookWithOffset:(NSInteger)offset 
                                            limit:(NSInteger)limit 
                                      andCallback:(void (^)(NSArray*, NSError*, STCancellation*))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/users/invite/facebook/collection.json"
                                                     post:NO
                                               authPolicy:STRestKitAuthPolicyWait
                                                   params:[NSDictionary dictionaryWithObjectsAndKeys:
                                                           [NSNumber numberWithInteger:offset], @"offset",
                                                           [NSNumber numberWithInteger:limit], @"limit",
                                                           nil]
                                                  mapping:[self facebookMapping]
                                              andCallback:block];
}

+ (STCancellation*)contactsFromTwitterWithOffset:(NSInteger)offset 
                                           limit:(NSInteger)limit 
                                     andCallback:(void (^)(NSArray*, NSError*, STCancellation*))block {
    return [[STRestKitLoader sharedInstance] loadWithPath:@"/users/invite/twitter/collection.json"
                                                     post:NO
                                               authPolicy:STRestKitAuthPolicyWait
                                                   params:[NSDictionary dictionaryWithObjectsAndKeys:
                                                           [NSNumber numberWithInteger:offset], @"offset",
                                                           [NSNumber numberWithInteger:limit], @"limit",
                                                           nil]
                                                  mapping:[self twitterMapping]
                                              andCallback:block];
}

@end
