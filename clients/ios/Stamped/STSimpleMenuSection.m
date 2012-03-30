//
//  STSimpleMenuSection.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenuSection.h"
#import "STSimpleMenuItem.h"

@implementation STSimpleMenuSection

@synthesize title = _title;
@synthesize desc = _desc;
@synthesize shortDesc = _shortDesc;
@synthesize items = _items;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenuSection class]];
  
  [mapping mapKeyPathsToAttributes:
   @"short_desc", @"shortDesc",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"desc",
   nil];
  
  [mapping mapRelationship:@"items" withMapping:[STSimpleMenuItem mapping]];
  
  return mapping;
}

@end
