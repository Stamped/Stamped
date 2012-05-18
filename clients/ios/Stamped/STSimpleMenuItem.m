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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _title = [[decoder decodeObjectForKey:@"title"] retain];
    _desc = [[decoder decodeObjectForKey:@"desc"] retain];
    _categories = [[decoder decodeObjectForKey:@"categories"] retain];
    _shortDesc = [[decoder decodeObjectForKey:@"shortDesc"] retain];
    _spicy = [decoder decodeIntegerForKey:@"spice"];
    _allergens = [[decoder decodeObjectForKey:@"allergens"] retain];
    _allergenFree = [[decoder decodeObjectForKey:@"allergenFree"] retain];
    _restrictions = [[decoder decodeObjectForKey:@"restrictions"] retain];
    _prices = [[decoder decodeObjectForKey:@"prices"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_title release];
  [_desc release];
  [_categories release];
  [_shortDesc release];
  [_allergens release];
  [_allergenFree release];
  [_restrictions release];
  [_prices release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.title forKey:@"title"];
  [encoder encodeObject:self.desc forKey:@"desc"];
  [encoder encodeObject:self.categories forKey:@"categories"];
  [encoder encodeObject:self.shortDesc forKey:@"shortDesc"];
  [encoder encodeInteger:self.spicy forKey:@"spicy"];
  [encoder encodeObject:self.allergens forKey:@"allergens"];
  [encoder encodeObject:self.allergenFree forKey:@"allergenFree"];
  [encoder encodeObject:self.restrictions forKey:@"restrictions"];
  [encoder encodeObject:self.prices forKey:@"prices"];
}

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
