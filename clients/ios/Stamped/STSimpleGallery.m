//
//  STSimpleGallery.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleGallery.h"
#import "STSimpleImageList.h"

@implementation STSimpleGallery

@synthesize layout = _layout;
@synthesize name = _name;
@synthesize images = _images;

-(id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _layout = [[decoder decodeObjectForKey:@"layout"] retain];
    _name = [[decoder decodeObjectForKey:@"name"] retain];
    _images = [[decoder decodeObjectForKey:@"images"] retain];
  }
  return self;
}

- (void)dealloc {
  [_layout release];
  [_name release];
  [_images release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.layout forKey:@"layout"];
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.images forKey:@"images"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGallery class]];
  
  [mapping mapAttributes:
   @"layout",
   @"name",
   nil];
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  
  return mapping;
}

@end
