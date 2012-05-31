//
//  STMenuItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STMenuPrice.h"

@protocol STMenuItem <NSObject>

@property (nonatomic, readonly, retain) NSString* title;
@property (nonatomic, readonly, retain) NSString* desc;
@property (nonatomic, readonly, retain) NSString* shortDesc;
@property (nonatomic, readonly, retain) NSArray* categories;
@property (nonatomic, readonly, retain) NSArray* allergens;
@property (nonatomic, readonly, retain) NSArray* allergenFree;
@property (nonatomic, readonly, retain) NSArray* restrictions;
@property (nonatomic, readonly, retain) NSNumber* spicy;
@property (nonatomic, readonly, retain) NSArray<STMenuPrice>* prices;

@end
