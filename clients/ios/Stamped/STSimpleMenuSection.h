//
//  STSimpleMenuSection.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMenuSection.h"

@interface STSimpleMenuSection : NSObject <STMenuSection, NSCoding>

@property (nonatomic, readwrite, retain) NSString* title;
@property (nonatomic, readwrite, retain) NSString* desc;
@property (nonatomic, readwrite, retain) NSString* shortDesc;
@property (nonatomic, readwrite, retain) NSArray<STMenuItem>* items;

+ (RKObjectMapping*)mapping;

@end
