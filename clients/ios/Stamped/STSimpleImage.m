//
//  STSimpleImage.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleImage.h"

@implementation STSimpleImage

@synthesize image = _image;
@synthesize width = _width;
@synthesize height = _height;
@synthesize source = _source;
@synthesize filter = _filter;

- (void)dealloc
{
  [_image release];
  [_width release];
  [_height release];
  [_source release];
  [_filter release];
  [super dealloc];
}


+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleImage class]];
  
  [mapping mapAttributes:
   @"image",
   @"width",
   @"height",
   @"source",
   @"filter",
   nil];
  
  return mapping;
}

@end
