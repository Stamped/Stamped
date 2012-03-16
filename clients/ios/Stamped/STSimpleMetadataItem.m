//
//  STSimpleMetadataItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMetadataItem.h"
#import "STSimpleAction.h"

@implementation STSimpleMetadataItem

@synthesize name = name_;
@synthesize value = value_;
@synthesize icon = icon_;
@synthesize link = link_;
@synthesize action = action_;

- (void)dealloc {
  self.name = nil;
  self.value = nil;
  self.icon = nil;
  self.link = nil;
  self.action = nil;
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMetadataItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"value",
   @"icon",
   @"link",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
