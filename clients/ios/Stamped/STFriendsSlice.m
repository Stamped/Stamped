//
//  STUserCollectionSlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STFriendsSlice.h"

@implementation STFriendsSlice

@synthesize distance = _distance;
@synthesize inclusive = _inclusive;

- (void)dealloc
{
  [_distance release];
  [_inclusive release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  if (self.distance) {
    [dict setObject:self.distance forKey:@"distance"];
  }
  if (self.inclusive) {
    [dict setObject:self.inclusive forKey:@"inclusive"];
  }
  return dict;
}


- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
  NSArray* keys = [NSArray arrayWithObjects:
                   @"distance",
                   @"inclusive",
                   nil];
  for (NSString* key in keys) {
    id value = [params objectForKey:key];
    if (value) {
      [self setValue:value forKey:key];
    }
  }
}

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STFriendsSlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.distance = self.distance;
  copy.inclusive = self.inclusive;
  return copy;
}

@end
