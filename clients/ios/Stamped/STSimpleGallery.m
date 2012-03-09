//
//  STSimpleGallery.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleGallery.h"
#import "STSimpleGalleryItem.h"

@implementation STSimpleGallery

@synthesize name = name_;
@synthesize data = data_;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGallery class]];
  
  [mapping mapAttributes:
   @"name",
   nil];
  
  [mapping mapRelationship:@"data" withMapping:[STSimpleGalleryItem mapping]];
  
  return mapping;
}

@end
