//
//  STSimpleEntity.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntity.h"

@implementation STSimpleEntity

@synthesize entityID = _entityID;
@synthesize title = _title;
@synthesize subtitle = _subtitle;
@synthesize category = _category;
@synthesize subcategory = _subcategory;
@synthesize coordinates = _coordinates;

- (void)dealloc
{
  [_entityID release];
  [_title release];
  [_subtitle release];
  [_category release];
  [_subcategory release];
  [_coordinates release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntity class]];
  
  [mapping mapKeyPathsToAttributes:
   @"entity_id", @"entityID",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"subtitle",
   @"category",
   @"subcategory",
   @"coordinates",
   nil];
  
  return mapping;
}

@end