//
//  STSimplePlaylistItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePlaylistItem.h"
#import "STSimpleSource.h"
#import "STSimpleAction.h"

@implementation STSimplePlaylistItem

@synthesize name = name_;
@synthesize length = length_;
@synthesize icon = icon_;
@synthesize entityID = _entityID;
@synthesize action = action_;

- (void)dealloc {
  self.name = nil;
  self.icon = nil;
  self.action = nil;
  self.entityID = nil;
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePlaylistItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"icon",
   @"length",
   nil];
  
  [mapping mapKeyPathsToAttributes:@"entity_id", @"entityID", nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
