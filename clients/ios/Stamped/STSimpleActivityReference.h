//
//  STSimpleActivityReference.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STActivityReference.h"

@interface STSimpleActivityReference : NSObject <STActivityReference>

@property (nonatomic, readwrite, copy) NSArray* indices;
@property (nonatomic, readwrite, copy) id<STAction> action;
@property (nonatomic, readwrite, copy) NSDictionary* format;

+ (RKObjectMapping*)mapping;

@end
