//
//  STSimpleGalleryItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleGalleryItem.h"
#import "STGalleryItem.h"
#import "STSimpleAction.h"

@implementation STSimpleGalleryItem

@synthesize image = _image;
@synthesize caption = _caption;
@synthesize action = _action;
@synthesize height = _height;
@synthesize width = _width;

- (void)dealloc {
  [_image release];
  [_caption release];
  [_action release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGalleryItem class]];
  
  [mapping mapAttributes:
   @"image",
   @"caption",
   @"height",
   @"width",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
