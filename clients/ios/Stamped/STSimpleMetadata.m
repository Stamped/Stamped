//
//  STSimpleMetadata.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMetadata.h"
#import "STSimpleMetadataItem.h"

@implementation STSimpleMetadata

@synthesize name = name_;
@synthesize data = data_;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMetadata class]];
  
  [mapping mapAttributes:
   @"name",
   nil];
  
  [mapping mapRelationship:@"data" withMapping:[STSimpleMetadataItem mapping]];
  
  return mapping;
}

@end
