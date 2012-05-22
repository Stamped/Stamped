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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _title = [[decoder decodeObjectForKey:@"title"] retain];
    _price = [[decoder decodeObjectForKey:@"price"] retain];
    _calories = [decoder decodeIntegerForKey:@"calories"];
    _unit = [[decoder decodeObjectForKey:@"unit"] retain];
    _currency = [[decoder decodeObjectForKey:@"currency"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_title release];
  [_price release];
  [_unit release];
  [_currency release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.title forKey:@"title"];
  [encoder encodeObject:self.price forKey:@"price"];
  [encoder encodeInteger:self.calories forKey:@"calories"];
  [encoder encodeObject:self.unit forKey:@"unit"];
  [encoder encodeObject:self.currency forKey:@"currency"];
}

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
