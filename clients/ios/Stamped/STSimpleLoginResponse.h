//
//  STSimpleLoginResponse.h
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STLoginResponse.h"
#import <RestKit/RestKit.h>

@interface STSimpleLoginResponse : NSObject <STLoginResponse, NSCoding>

@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, copy) NSString* token;

+ (RKObjectMapping*)mapping;

@end
