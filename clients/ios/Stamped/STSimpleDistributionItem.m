//
//  STSimpleDistributionItem.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleDistributionItem.h"

@implementation STSimpleDistributionItem

@synthesize category = _category;
@synthesize count = _count;
@synthesize name = _name;
@synthesize icon = _icon;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _category = [[decoder decodeObjectForKey:@"category"] retain];
    _count = [[decoder decodeObjectForKey:@"count"] retain];
    _name = [[decoder decodeObjectForKey:@"name"] retain];
    _icon = [[decoder decodeObjectForKey:@"icon"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_category release];
  [_count release];
  [_name release];
  [_icon release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.category forKey:@"category"];
  [encoder encodeObject:self.count forKey:@"count"];
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.icon forKey:@"icon"];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleDistributionItem class]];
  
  [mapping mapAttributes:
   @"category",
   @"count",
   @"name",
   @"icon",
   nil];
  
  return mapping;
}

@end
