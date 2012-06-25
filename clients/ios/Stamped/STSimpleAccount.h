//
//  STSimpleAccount.h
//  Stamped
//
//  Created by Landon Judkins on 6/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STAccount.h"

@interface STSimpleAccount : NSObject <STAccount, NSCoding>

@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSString* email;
@property (nonatomic, readwrite, copy) NSString* authService;
@property (nonatomic, readwrite, copy) NSString* screenName;
@property (nonatomic, readwrite, copy) NSNumber* privacy;
@property (nonatomic, readwrite, copy) NSString* phone;

+ (RKObjectMapping*)mapping;

@end
