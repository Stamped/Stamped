//
//  STSimpleMenuPrice.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenuPrice.h"

@implementation STSimpleMenuPrice

@synthesize title = _title;
@synthesize price = _price;
@synthesize calories = _calories;
@synthesize unit = _unit;
@synthesize currency = _currency;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenuPrice class]];
  
  [mapping mapAttributes:
   @"title",
   @"price",
   @"calories",
   @"unit",
   @"currency",
   nil];

  return mapping;
}

@end
