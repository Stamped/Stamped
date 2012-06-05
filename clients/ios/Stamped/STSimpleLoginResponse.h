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

@property (nonatomic, readwrite, retain) id<STUserDetail> user;
@property (nonatomic, readwrite, retain) id<STOAuthToken> token;

+ (RKObjectMapping*)mapping;

@end
