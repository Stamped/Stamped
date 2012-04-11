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

- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
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
    id value = [params objectForKey:key];
    if (value) {
      [self setValue:value forKey:key];
    }
  }
}

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STGenericCollectionSlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.query = self.query;
  copy.category = self.category;
  copy.subcategory = self.subcategory;
  copy.viewport = self.viewport;
  copy.quality = self.quality;
  copy.deleted = self.deleted;
  copy.comments = self.comments;
  copy.unique = self.unique;
  return copy;
}
  
@end
