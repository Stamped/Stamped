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

- (void)importDictionaryParams:(NSDictionary*)params {
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
    id value = [params objectForKey:key];
    if (value) {
      [self setValue:value forKey:key];
    }
  }
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

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STGenericSlice* copy = [[[self class] alloc] init];
  copy.limit = limit;
  copy.offset = offset;
  copy.sort = self.sort;
  copy.reverse = self.reverse;
  copy.coordinates = self.coordinates;
  copy.since = self.since;
  copy.before = self.before;
  return copy;
}

@end
