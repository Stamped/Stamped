//
//  STConsumptionSlice.m
//  Stamped
//
//  Created by Landon Judkins on 5/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionSlice.h"

@implementation STConsumptionSlice

@synthesize scope = scope_;
@synthesize filter = filter_;

- (void)dealloc
{
  [scope_ release];
  [filter_ release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  if (self.scope) {
    [dict setObject:self.scope forKey:@"scope"];
  }
  if (self.filter) {
    [dict setObject:self.filter forKey:@"filter"];
  }
  return dict;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
  if ([params objectForKey:@"scope"]) {
    self.scope = [params objectForKey:@"scope"];
  }
  if ([params objectForKey:@"filter"]) {
    self.filter = [params objectForKey:@"filter"];
  }
}

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STConsumptionSlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.scope = self.scope;
  copy.filter = self.filter;
  return copy;
}


@end
