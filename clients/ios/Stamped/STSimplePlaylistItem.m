//
//  STSimplePlaylistItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePlaylistItem.h"
#import "STSimpleSource.h"

@implementation STSimplePlaylistItem

@synthesize name = name_;
@synthesize num = num_;
@synthesize length = length_;
@synthesize icon = icon_;
@synthesize link = link_;
@synthesize sources = sources_;

- (void)dealloc {
  self.name = nil;
  self.icon = nil;
  self.link = nil;
  self.sources = nil;
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePlaylistItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"num",
   @"icon",
   @"link",
   nil];
  
  [mapping mapRelationship:@"sources" withMapping:[STSimpleSource mapping]];
  
  return mapping;
}

@end
