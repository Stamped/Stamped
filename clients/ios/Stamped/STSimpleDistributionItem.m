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

- (void)dealloc
{
  [_category release];
  [_count release];
  [_name release];
  [_icon release];
  [super dealloc];
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
