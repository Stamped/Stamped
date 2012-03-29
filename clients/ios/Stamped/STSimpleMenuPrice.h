//
//  STSimpleMenuPrice.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMenuPrice.h"

@interface STSimpleMenuPrice : NSObject <STMenuPrice>

@property (nonatomic, readwrite, retain) NSString* title;
@property (nonatomic, readwrite, retain) NSString* price;
@property (nonatomic, readwrite, assign) NSInteger calories;
@property (nonatomic, readwrite, assign) NSString* unit;
@property (nonatomic, readwrite, assign) NSString* currency;

+ (RKObjectMapping*)mapping;

@end
