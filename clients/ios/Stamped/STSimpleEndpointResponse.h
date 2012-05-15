//
//  STSimpleEndpointResponse.h
//  Stamped
//
//  Created by Landon Judkins on 5/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEndpointResponse.h"
#import <RestKit/RestKit.h>

@interface STSimpleEndpointResponse : NSObject <STEndpointResponse, NSCoding>

@property (nonatomic, readwrite, retain) id<STAction> action;

+ (RKObjectMapping*)mapping;

@end
