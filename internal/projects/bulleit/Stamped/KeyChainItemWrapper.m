//
//  KeyChainItemWrapper.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "KeychainItemWrapper.h"

#import <Security/Security.h>

@interface KeychainItemWrapper ()
- (NSMutableDictionary*)secItemFormatToDictionary:(NSDictionary*)dictionaryToConvert;
- (NSMutableDictionary*)dictionaryToSecItemFormat:(NSDictionary*)dictionaryToConvert;
- (void)writeToKeychain;
@end

@implementation KeychainItemWrapper

- (id)initWithIdentifier:(NSString*)identifier {
  self = [super init];
  if (self) {
    genericPasswordQuery_ = [[NSMutableDictionary alloc] init];
		[genericPasswordQuery_ setObject:(id)kSecClassGenericPassword forKey:(id)kSecClass];
    [genericPasswordQuery_ setObject:identifier forKey:(id)kSecAttrGeneric];
    [genericPasswordQuery_ setObject:(id)kSecMatchLimitOne forKey:(id)kSecMatchLimit];
    [genericPasswordQuery_ setObject:(id)kCFBooleanTrue forKey:(id)kSecReturnAttributes];

    NSDictionary* tempQuery = [NSDictionary dictionaryWithDictionary:genericPasswordQuery_];

    NSMutableDictionary* outDictionary = nil;

    if (SecItemCopyMatching((CFDictionaryRef)tempQuery, (CFTypeRef*)&outDictionary) == noErr) {
      keychainItemData_ = [[self secItemFormatToDictionary:outDictionary] retain];
		} else {
      [self resetKeychainItem];
			[keychainItemData_ setObject:identifier forKey:(id)kSecAttrGeneric];
    }

		[outDictionary release];
  }
	return self;
}

- (void)dealloc {
  [keychainItemData_ release];
  [genericPasswordQuery_ release];

	[super dealloc];
}

- (void)setObject:(id)inObject forKey:(id)key {
  if (inObject == nil)
    return;

  id currentObject = [keychainItemData_ objectForKey:key];
  if (![currentObject isEqual:inObject]) {
    [keychainItemData_ setObject:inObject forKey:key];
    [self writeToKeychain];
  }
}

- (id)objectForKey:(id)key {
  return [keychainItemData_ objectForKey:key];
}

- (void)resetKeychainItem {
	OSStatus result = noErr;
  if (!keychainItemData_) {
    keychainItemData_ = [[NSMutableDictionary alloc] init];
  } else if (keychainItemData_) {
    NSMutableDictionary* tempDictionary = [self dictionaryToSecItemFormat:keychainItemData_];
		result = SecItemDelete((CFDictionaryRef)tempDictionary);
    NSAssert(result == noErr || result == errSecItemNotFound, @"Problem deleting current dictionary.");
  }
  [keychainItemData_ setObject:@"" forKey:(id)kSecAttrAccount];
  [keychainItemData_ setObject:@"" forKey:(id)kSecAttrLabel];
  [keychainItemData_ setObject:@"" forKey:(id)kSecAttrDescription];
  [keychainItemData_ setObject:@"" forKey:(id)kSecValueData];
}

- (NSMutableDictionary*)dictionaryToSecItemFormat:(NSDictionary*)dictionaryToConvert {
  NSMutableDictionary* returnDictionary = [NSMutableDictionary dictionaryWithDictionary:dictionaryToConvert];
  [returnDictionary setObject:(id)kSecClassGenericPassword forKey:(id)kSecClass];
  NSString* passwordString = [dictionaryToConvert objectForKey:(id)kSecValueData];
  [returnDictionary setObject:[passwordString dataUsingEncoding:NSUTF8StringEncoding] forKey:(id)kSecValueData];
  
  return returnDictionary;
}

- (NSMutableDictionary*)secItemFormatToDictionary:(NSDictionary*)dictionaryToConvert {
  NSMutableDictionary* returnDictionary = [NSMutableDictionary dictionaryWithDictionary:dictionaryToConvert];
  [returnDictionary setObject:(id)kCFBooleanTrue forKey:(id)kSecReturnData];
  [returnDictionary setObject:(id)kSecClassGenericPassword forKey:(id)kSecClass];
  NSData* passwordData = NULL;
  if (SecItemCopyMatching((CFDictionaryRef)returnDictionary, (CFTypeRef*)&passwordData) == noErr) {
    [returnDictionary removeObjectForKey:(id)kSecReturnData];
    NSString* password = [[[NSString alloc] initWithBytes:[passwordData bytes] length:[passwordData length] 
                                                 encoding:NSUTF8StringEncoding] autorelease];
    [returnDictionary setObject:password forKey:(id)kSecValueData];
  } else {
    NSAssert(NO, @"Serious error, no matching item found in the keychain.\n");
  }

  [passwordData release];

	return returnDictionary;
}

- (void)writeToKeychain {
  NSDictionary* attributes = NULL;
  NSMutableDictionary* updateItem = NULL;
	OSStatus result;

  if (SecItemCopyMatching((CFDictionaryRef)genericPasswordQuery_, (CFTypeRef*)&attributes) == noErr) {
    updateItem = [NSMutableDictionary dictionaryWithDictionary:attributes];
    [updateItem setObject:[genericPasswordQuery_ objectForKey:(id)kSecClass] forKey:(id)kSecClass];
    
    NSMutableDictionary* tempCheck = [self dictionaryToSecItemFormat:keychainItemData_];
    [tempCheck removeObjectForKey:(id)kSecClass];

    result = SecItemUpdate((CFDictionaryRef)updateItem, (CFDictionaryRef)tempCheck);
		NSAssert(result == noErr, @"Couldn't update the Keychain Item.");
  } else {
    // No previous item found; add the new one.
    result = SecItemAdd((CFDictionaryRef)[self dictionaryToSecItemFormat:keychainItemData_], NULL);
		NSAssert(result == noErr, @"Couldn't add the Keychain Item. Error code %d", result);
  }
}

@end
