//
//  STSimpleActionItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActionItem.h"
#import "STSimpleAction.h"

@implementation STSimpleActionItem

@synthesize icon = icon_;
@synthesize name = name_;
@synthesize action = action_;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActionItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"icon",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

- (void)dealloc {
  self.name = nil;
  self.icon = nil;
  self.action = nil;
  [super dealloc];
}


@end
