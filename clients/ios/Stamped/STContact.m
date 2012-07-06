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

@synthesize userDetail = _userDetail;

- (void)dealloc
{
    [_name release];
    [_phoneNumbers release];
    [_emailAddresses release];
    [_userDetail release];
    [super dealloc];
}

+ (NSArray*)contactsForOffset:(NSInteger)offset andLimit:(NSInteger)limit nextOffset:(NSInteger*)nextOffset finished:(BOOL*)finished {
    NSMutableArray* contacts = [NSMutableArray array];
    ABAddressBookRef addressBook = ABAddressBookCreate();
    CFArrayRef people = ABAddressBookCopyArrayOfAllPeople(addressBook);
    CFIndex numPeople = ABAddressBookGetPersonCount(addressBook);
    NSInteger i = offset;
    while (contacts.count < limit && i < numPeople) {
        
        ABRecordRef person = CFArrayGetValueAtIndex(people, i);
        STContact* contact = [[[STContact alloc] init] autorelease];
        
        CFStringRef nameRef = ABRecordCopyCompositeName(person);
        contact.name = (NSString*)nameRef;
        CFRelease(nameRef);
        
        ABMultiValueRef phoneNumberProperty = ABRecordCopyValue(person, kABPersonPhoneProperty);
        NSArray* phoneNumbers = (NSArray*)ABMultiValueCopyArrayOfAllValues(phoneNumberProperty);
        NSMutableArray* sanitizedNumbers = [NSMutableArray array];
        for (NSString* num in phoneNumbers) {
            NSString* sanitized = [Util sanitizedPhoneNumberFromString:num];
            if (sanitized) {
                [sanitizedNumbers addObject:sanitized];
            }
        }
        contact.phoneNumbers = sanitizedNumbers;
        CFRelease(phoneNumberProperty);
        [phoneNumbers release];
        
        ABMultiValueRef emailProperty = ABRecordCopyValue(person, kABPersonEmailProperty);
        NSArray* emails = (NSArray*)ABMultiValueCopyArrayOfAllValues(emailProperty);
        CFRelease(emailProperty);
        contact.emailAddresses = emails;
        [emails release];
        if (contact.name.length && (contact.phoneNumbers.count || contact.emailAddresses.count)) {
            [contacts addObject:contact];
        }
        i++;
    }
    *finished = i == numPeople;
    
    CFRelease(addressBook);
    CFRelease(people);
    return contacts;
}

@end
