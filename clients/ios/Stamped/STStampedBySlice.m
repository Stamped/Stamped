//
//  STStampedBySlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedBySlice.h"

@implementation STStampedBySlice

@synthesize entityID = _entityID;
@synthesize group = _group;

- (void)dealloc
{
  [_entityID release];
  [_group release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  if (self.entityID) {
    [dict setObject:self.entityID forKey:@"entity_id"];
  }
  if (self.group) {
    [dict setObject:self.group forKey:@"group"];
  }
  return dict;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
  if ([params objectForKey:@"entity_id"]) {
    self.entityID = [params objectForKey:@"entity_id"];
  }
  if ([params objectForKey:@"group"]) {
    self.group = [params objectForKey:@"group"];
  }
}

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STStampedBySlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.entityID = self.entityID;
  copy.group = self.group;
  return copy;
}

+ (STStampedBySlice*)standardSliceWithEntityID:(NSString*)entityID {
  STStampedBySlice* slice = [[[STStampedBySlice alloc] init] autorelease];
  slice.limit = [NSNumber numberWithInteger:20];
  slice.entityID = entityID;
  return slice;
}


@end
