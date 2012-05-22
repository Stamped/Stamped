//
//  STSimpleMenuItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMenuItem.h"

@interface STSimpleMenuItem : NSObject <STMenuItem, NSCoding>

@property (nonatomic, readwrite, retain) NSString* title;
@property (nonatomic, readwrite, retain) NSString* desc;
@property (nonatomic, readwrite, retain) NSString* shortDesc;
@property (nonatomic, readwrite, retain) NSArray* categories;
@property (nonatomic, readwrite, retain) NSArray* allergens;
@property (nonatomic, readwrite, retain) NSArray* allergenFree;
@property (nonatomic, readwrite, retain) NSArray* restrictions;
@property (nonatomic, readwrite, assign) NSInteger spicy;
@property (nonatomic, readwrite, retain) NSArray<STMenuPrice>* prices;

+ (RKObjectMapping*)mapping;

@end
