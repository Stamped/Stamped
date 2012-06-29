//
//  STSimpleLinkedAccounts.h
//  Stamped
//
//  Created by Landon Judkins on 6/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STLinkedAccounts.h"

@interface STSimpleLinkedAccounts : NSObject <STLinkedAccounts, NSCoding>

@property (nonatomic, readwrite, retain) id<STLinkedAccount> facebook;
@property (nonatomic, readwrite, retain) id<STLinkedAccount> twitter;
@property (nonatomic, readwrite, retain) id<STLinkedAccount> rdio;
@property (nonatomic, readwrite, retain) id<STLinkedAccount> spotify;
@property (nonatomic, readwrite, retain) id<STLinkedAccount> netflix;

+ (RKObjectMapping*)mapping;

@end
