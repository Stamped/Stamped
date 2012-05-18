//
//  STSimpleCredit.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STCredit.h"

@interface STSimpleCredit : NSObject <STCredit, NSCoding>

@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, copy) NSString* screenName;
@property (nonatomic, readwrite, copy) NSString* stampID;
@property (nonatomic, readwrite, copy) NSString* colorPrimary;
@property (nonatomic, readwrite, copy) NSString* colorSecondary;
@property (nonatomic, readwrite, copy) NSString* privacy;

+ (RKObjectMapping*)mapping;

@end
