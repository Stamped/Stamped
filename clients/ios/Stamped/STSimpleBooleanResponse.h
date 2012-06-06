//
//  STSimpleBooleanResponse.h
//  Stamped
//
//  Created by Landon Judkins on 6/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STBooleanResponse.h"
#import <RestKit/RestKit.h>

@interface STSimpleBooleanResponse : NSObject <STBooleanResponse, NSCoding>

@property (nonatomic, readwrite, copy) NSNumber* result;

+ (RKObjectMapping*)mapping;

@end
