//
//  STSimpleDistributionItem.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STDistributionItem.h"

@interface STSimpleDistributionItem : NSObject <STDistributionItem, NSCoding>

@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSNumber* count;
@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSString* icon;

+ (RKObjectMapping*)mapping;

@end
