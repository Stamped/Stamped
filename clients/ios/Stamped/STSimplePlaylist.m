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

- (void)dealloc {
  self.name = nil;
  self.data = nil;
  [super dealloc];
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
