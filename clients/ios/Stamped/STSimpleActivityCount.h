//
//  STSimpleActivityCount.h
//  Stamped
//
//  Created by Landon Judkins on 5/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STActivityCount.h"

@interface STSimpleActivityCount : NSObject <STActivityCount, NSCoding>

@property (nonatomic, readwrite, copy) NSNumber* numberUnread;

+ (RKObjectMapping*)mapping;

@end
