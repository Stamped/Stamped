//
//  STSimpleContentItem.m
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleContentItem.h"

@implementation STSimpleContentItem

@synthesize modified = modified_;
@synthesize blurb = blurb_;
@synthesize created = created_;

- (void)dealloc
{
  [modified_ release];
  [blurb_ release];
  [created_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleContentItem class]];
  
  [mapping mapAttributes:
   @"modified",
   @"blurb",
   @"created",
   nil];
  
  return mapping;
}

@end
