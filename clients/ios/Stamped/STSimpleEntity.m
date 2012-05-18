//
//  STSimpleEntity.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntity.h"
#import "STSimpleImage.h"
#import "STSimpleImageList.h"

@implementation STSimpleEntity

@synthesize entityID = _entityID;
@synthesize title = _title;
@synthesize subtitle = _subtitle;
@synthesize category = _category;
@synthesize subcategory = _subcategory;
@synthesize coordinates = _coordinates;

@synthesize images = images_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _entityID = [[decoder decodeObjectForKey:@"entityID"] retain];
    _title = [[decoder decodeObjectForKey:@"title"] retain];
    _subtitle = [[decoder decodeObjectForKey:@"subtitle"] retain];
    _category = [[decoder decodeObjectForKey:@"category"] retain];
    _subcategory = [[decoder decodeObjectForKey:@"subcategory"] retain];
    _coordinates = [[decoder decodeObjectForKey:@"coordinates"] retain];
    images_ = [[decoder decodeObjectForKey:@"images"] retain];
  }
  return self;
}

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

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.entityID forKey:@"entityID"];
  [encoder encodeObject:self.title forKey:@"title"];
  [encoder encodeObject:self.subtitle forKey:@"subtitle"];
  [encoder encodeObject:self.category forKey:@"category"];
  [encoder encodeObject:self.subcategory forKey:@"subcategory"];
  [encoder encodeObject:self.coordinates forKey:@"coordinates"];
  [encoder encodeObject:self.images forKey:@"images"];
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
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  
  return mapping;
}

@end
