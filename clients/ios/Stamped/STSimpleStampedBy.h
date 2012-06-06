//
//  STSimpleStampedBy.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampedBy.h"
#import <RestKit/RestKit.h>

@interface STSimpleStampedBy : NSObject <STStampedBy, NSCoding>

@property (nonatomic, readwrite, retain) id<STStampedByGroup> friends;
@property (nonatomic, readwrite, retain) id<STStampedByGroup> everyone;

+ (RKObjectMapping*)mapping;

@end
