//
//  KeyChainItemWrapper.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface KeychainItemWrapper : NSObject {
 @private
  NSMutableDictionary* keychainItemData_;
  NSMutableDictionary* genericPasswordQuery_;
}

// Designated initializer.
- (id)initWithIdentifier:(NSString*)identifier;
- (void)setObject:(id)inObject forKey:(id)key;
- (id)objectForKey:(id)key;

// Initializes and resets the default generic keychain item data.
- (void)resetKeychainItem;

@end