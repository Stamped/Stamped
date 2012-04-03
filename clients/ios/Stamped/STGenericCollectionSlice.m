//
//  STGenericCollectionSlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCollectionSlice.h"

@implementation STGenericCollectionSlice

@synthesize query = _query;
@synthesize category = _category;
@synthesize subcategory = _subcategory;
@synthesize viewport = _viewport;
@synthesize quality = _quality;
@synthesize deleted = _deleted;
@synthesize comments = _comments;
@synthesize unique = _unique;

- (void)dealloc
{
  [_query release];
  [_category release];
  [_subcategory release];
  [_viewport release];
  [_quality release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  NSArray* keys = [NSArray arrayWithObjects:
                   @"query",
                   @"category",
                   @"subcategory",
                   @"viewport",
                   @"quality",
                   @"deleted",
                   @"comments",
                   @"unique",
                   nil];
  for (NSString* key in keys) {
    id value = [self valueForKey:key];
    if (value) {
      [dict setObject:value forKey:key];
    }
  }
  return dict;
}

@end
