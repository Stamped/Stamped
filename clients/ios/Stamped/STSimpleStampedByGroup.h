//
//  STSimpleStampedByGroup.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampedByGroup.h"
#import <RestKit/RestKit.h>

@interface STSimpleStampedByGroup : NSObject <STStampedByGroup, NSCoding>

@property (nonatomic, readwrite, copy) NSNumber* count;
@property (nonatomic, readonly, retain) NSArray<STStampPreview>* stampPreviews;

+ (RKObjectMapping*)mapping;

@end
