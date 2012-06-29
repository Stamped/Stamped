//
//  STSimpleLinkedAccount.h
//  Stamped
//
//  Created by Landon Judkins on 6/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STLinkedAccount.h"

@interface STSimpleLinkedAccount : NSObject <STLinkedAccount, NSCoding>

@property (nonatomic, readwrite, copy) NSString* serviceName;
@property (nonatomic, readwrite, copy) NSString* linkedUserID;
@property (nonatomic, readwrite, copy) NSString* linkedScreenName;
@property (nonatomic, readwrite, copy) NSString* linkedName;
@property (nonatomic, readwrite, copy) NSString* token;
@property (nonatomic, readwrite, copy) NSString* secret;
@property (nonatomic, readwrite, copy) NSDate* tokenExpiration;

+ (RKObjectMapping*)mapping;

@end
