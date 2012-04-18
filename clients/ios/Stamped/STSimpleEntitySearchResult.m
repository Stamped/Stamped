//
//  STSimpleEntitySearchResult.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntitySearchResult.h"

@implementation STSimpleEntitySearchResult

@synthesize searchID = searchID_;
@synthesize title = title_;
@synthesize subtitle = subtitle_;
@synthesize category = category_;
@synthesize distance = distance_;

- (void)dealloc
{
  [searchID_ release];
  [title_ release];
  [subtitle_ release];
  [category_ release];
  [distance_ release];
  [super dealloc];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntitySearchResult class]];
  
  [mapping mapAttributes:
   @"title",
   @"subtitle",
   @"category",
   @"distance",
   nil];
  
  [mapping mapKeyPathsToAttributes:@"search_id", @"searchID", nil];
  
  return mapping;
}

@end
