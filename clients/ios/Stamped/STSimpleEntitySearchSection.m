//
//  STSimpleEntitySearchSection.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntitySearchSection.h"
#import "STSimpleEntitySearchResult.h"

@implementation STSimpleEntitySearchSection

@synthesize name = name_;
@synthesize results = results_;

- (void)dealloc
{
  [name_ release];
  [results_ release];
  [super dealloc];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntitySearchSection class]];
  
  [mapping mapAttributes:
   @"name",
   nil];
  
  [mapping mapRelationship:@"results" withMapping:[STSimpleEntitySearchResult mapping]];
  
  return mapping;
}

@end
