//
//  STSimpleImageList.m
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleImageList.h"
#import "STSimpleImage.h"
#import "STSimpleAction.h"

@implementation STSimpleImageList

@synthesize sizes = sizes_;
@synthesize caption = caption_;
@synthesize action = action_;

- (void)dealloc
{
  [sizes_ release];
  [caption_ release];
  [action_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleImageList class]];
  
  [mapping mapAttributes:
   @"caption",
   nil];
  
  [mapping mapRelationship:@"sizes" withMapping:[STSimpleImage mapping]];
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
