//
//  STSimpleEntity.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntity.h"
#import "STSimpleImage.h"

@implementation STSimpleEntity

@synthesize entityID = _entityID;
@synthesize title = _title;
@synthesize subtitle = _subtitle;
@synthesize category = _category;
@synthesize subcategory = _subcategory;
@synthesize coordinates = _coordinates;

@synthesize images = images_;

- (void)dealloc
{
  [_entityID release];
  [_title release];
  [_subtitle release];
  [_category release];
  [_subcategory release];
  [_coordinates release];
  [images_ release];
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
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImage mapping]];
  
  return mapping;
}

@end
