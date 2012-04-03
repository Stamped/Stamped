//
//  STGenericSlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericSlice.h"

@implementation STGenericSlice

@synthesize limit = _limit;
@synthesize offset = _offset;
@synthesize sort = _sort;
@synthesize reverse = _reverse;
@synthesize coordinates = _coordinates;
@synthesize since = _since;
@synthesize before = _before;

- (void)dealloc
{
  [_limit release];
  [_offset release];
  [_sort release];
  [_reverse release];
  [_coordinates release];
  [_since release];
  [_before release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [NSMutableDictionary dictionary];
  NSArray* keys = [NSArray arrayWithObjects:
                   @"limit",
                   @"offset",
                   @"sort",
                   @"reverse",
                   @"coordinates",
                   @"since",
                   @"before",
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
