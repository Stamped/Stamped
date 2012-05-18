//
//  STSimpleEntity.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import <RestKit/RestKit.h>

@interface STSimpleEntity : NSObject <STEntity, NSCoding>

@property (nonatomic, readwrite, retain) NSString* entityID;
@property (nonatomic, readwrite, retain) NSString* title;
@property (nonatomic, readwrite, retain) NSString* subtitle;
@property (nonatomic, readwrite, retain) NSString* category;
@property (nonatomic, readwrite, retain) NSString* subcategory;
@property (nonatomic, readwrite, retain) NSString* coordinates;

@property (nonatomic, readwrite, copy) NSArray<STImageList>* images;

+ (RKObjectMapping*)mapping;

@end
