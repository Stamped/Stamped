//
//  STSimpleSubmenu.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleSubmenu.h"
#import "STSimpleTimes.h"
#import "STSimpleMenuSection.h"

@implementation STSimpleSubmenu

@synthesize title = _title;
@synthesize times = _times;
@synthesize footnote = _footnote;
@synthesize desc = _desc;
@synthesize shortDesc = _shortDesc;
@synthesize sections = _sections;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleSubmenu class]];
  
  [mapping mapKeyPathsToAttributes:
   @"short_desc", @"shortDesc",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"footnote",
   @"desc",
   nil];
  
  [mapping mapRelationship:@"times" withMapping:[STSimpleTimes mapping]];
  [mapping mapRelationship:@"sections" withMapping:[STSimpleMenuSection mapping]];
  
  return mapping;
}

@end
