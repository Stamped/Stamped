//
//  STSimpleMenu.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenu.h"
#import "STSimpleSubmenu.h"

@implementation STSimpleMenu

@synthesize disclaimer = _disclaimer;
@synthesize attributionImage = _attributionImage;
@synthesize attributionImageLink = _attributionImageLink;
@synthesize menus = _menus;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenu class]];
  
  [mapping mapKeyPathsToAttributes:
   @"attribution_image", @"attributionImage",
   @"attribution_image_link", @"attributionImageLink",
   nil];
  
  [mapping mapAttributes:
   @"disclaimer",
   nil];
  
  [mapping mapRelationship:@"menus" withMapping:[STSimpleSubmenu mapping]];
  
  return mapping;
}

@end
