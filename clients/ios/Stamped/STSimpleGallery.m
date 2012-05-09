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

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGallery class]];
  
  [mapping mapAttributes:
   @"layout",
   @"name",
   nil];
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  
  return mapping;
}

- (void)dealloc {
  [_layout release];
  [_name release];
  [_images release];
  [super dealloc];
}

@end
