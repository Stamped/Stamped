//
//  STSimpleUser.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STUser.h"

@interface STSimpleUser : NSObject <STUser>

@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, copy) NSString* screenName;
@property (nonatomic, readwrite, copy) NSString* colorPrimary;
@property (nonatomic, readwrite, copy) NSString* colorSecondary;
@property (nonatomic, readwrite, copy) NSNumber* privacy;
@property (nonatomic, readwrite, copy) NSString* imageURL;

+ (RKObjectMapping*)mapping;

@end
