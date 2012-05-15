//
//  STSimpleActivityObject.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STActivityObjects.h"

@interface STSimpleActivityObjects : NSObject <STActivityObjects, NSCoding>

@property (nonatomic, readwrite, copy) NSArray<STStamp>* stamps;
@property (nonatomic, readwrite, copy) NSArray<STEntity>* entities;
@property (nonatomic, readwrite, copy) NSArray<STUser>* users;
@property (nonatomic, readwrite, copy) NSArray<STComment>* comments;

+ (RKObjectMapping*)mapping;

@end
