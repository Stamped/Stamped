//
//  STSimpleMenuItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenuItem.h"
#import "STSimpleMenuPrice.h"

@implementation STSimpleMenuItem

@synthesize title = _title;
@synthesize desc = _desc;
@synthesize categories = _categories;
@synthesize shortDesc = _shortDesc;
@synthesize spicy = _spicy;
@synthesize allergens = _allergens;
@synthesize allergenFree = _allergenFree;
@synthesize restrictions = _restrictions;
@synthesize prices = _prices;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenuItem class]];
  
  [mapping mapKeyPathsToAttributes:
   @"short_desc", @"shortDesc",
   @"allergen_free", @"allergenFree",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"desc",
   @"categories",
   @"spicy",
   @"allergens",
   @"restrictions",
   nil];
  
  [mapping mapRelationship:@"prices" withMapping:[STSimpleMenuPrice mapping]];
  
  return mapping;
}

@end
