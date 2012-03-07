//
//  STSimpleAction.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleAction.h"

@implementation STSimpleAction

@synthesize action = action_;
@synthesize name = name_;
@synthesize icon = icon_;
@synthesize sources = sources_;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleGalleryItem class]];
  
  [mapping mapAttributes:
   @"action",
   @"name",
   @"icon",
   nil];
  
  [mapping mapRelationship:@"sources" withMapping:[STSimpleSource mapping]];
  
  return mapping;
}

@end
