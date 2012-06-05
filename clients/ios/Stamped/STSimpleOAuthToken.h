//
//  STSimpleOAuthToken.h
//  Stamped
//
//  Created by Landon Judkins on 6/1/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STOAuthToken.h"

@interface STSimpleOAuthToken : NSObject <STOAuthToken, NSCoding>

@property (nonatomic, readwrite, copy) NSString* accessToken;
@property (nonatomic, readwrite, copy) NSString* refreshToken;
@property (nonatomic, readwrite, copy) NSNumber* lifespanInSeconds;

+ (RKObjectMapping*)mapping;

@end
