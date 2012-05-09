//
//  STSimpleContentItem.m
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleContentItem.h"
#import "STSimpleImageList.h"

@implementation STSimpleContentItem

@synthesize modified = modified_;
@synthesize blurb = blurb_;
@synthesize created = created_;
@synthesize images = images_;

- (void)dealloc
{
  [modified_ release];
  [blurb_ release];
  [created_ release];
  [images_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleContentItem class]];
  
  [mapping mapAttributes:
   @"modified",
   @"blurb",
   @"created",
   nil];
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  
  return mapping;
}

@end
