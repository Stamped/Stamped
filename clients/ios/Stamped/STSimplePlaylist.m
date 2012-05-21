//
//  STSimplePlaylist.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePlaylist.h"
#import "STSimplePlaylistItem.h"

@implementation STSimplePlaylist

@synthesize name = name_;
@synthesize overflow = overflow_;
@synthesize data = data_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    overflow_ = [decoder decodeIntegerForKey:@"overflow"];
    data_ = [[decoder decodeObjectForKey:@"data"] retain];
  }
  return self;
}

- (void)dealloc {
  self.name = nil;
  self.data = nil;
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeInteger:self.overflow forKey:@"overflow"];
  [encoder encodeObject:self.data forKey:@"data"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePlaylist class]];
  
  [mapping mapAttributes:
   @"name",
   @"overflow",
   nil];
  
  [mapping mapRelationship:@"data" withMapping:[STSimplePlaylistItem mapping]];
  
  return mapping;
}

@end
