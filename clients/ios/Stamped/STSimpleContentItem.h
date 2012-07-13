//
//  STSimpleContentItem.h
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STContentItem.h"

@interface STSimpleContentItem : NSObject <STContentItem, NSCoding>

@property (nonatomic, readwrite, copy) NSDate* modified;
@property (nonatomic, readwrite, copy) NSString* blurb;
@property (nonatomic, readwrite, copy) NSArray<STActivityReference>* blurbReferences;
@property (nonatomic, readwrite, copy) NSDate* created;
@property (nonatomic, readwrite, copy) NSArray<STImageList>* images;

+ (RKObjectMapping*)mapping;

@end
