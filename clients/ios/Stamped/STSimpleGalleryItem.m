//
//  STSimpleGalleryItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleGalleryItem.h"
#import "STGalleryItem.h"

@implementation STSimpleGalleryItem

@synthesize image = image_;
@synthesize caption = caption_;
@synthesize link = link_;
@synthesize linkType = linkType_;
@synthesize height = height_;
@synthesize width = width_;

- (void)dealloc {
  self.image = nil;
  self.caption = nil;
  self.link = nil;
  self.linkType = nil;
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGalleryItem class]];
  
  [mapping mapKeyPathsToAttributes:
   @"link_type", @"linkType",
   nil];
  
  [mapping mapAttributes:
   @"image",
   @"caption",
   @"link",
   @"height",
   @"width",
   nil];
  
  return mapping;
}

@end
