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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    length_ = [decoder decodeIntegerForKey:@"length"];
    icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
    _entityID = [[decoder decodeObjectForKey:@"entityID"] retain];
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
  }
  return self;
}

- (void)dealloc {
  self.name = nil;
  self.icon = nil;
  self.action = nil;
  self.entityID = nil;
  
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeInteger:self.length forKey:@"length"];
  [encoder encodeObject:self.icon forKey:@"icon"];
  [encoder encodeObject:self.action forKey:@"action"];
  [encoder encodeObject:self.entityID forKey:@"entityID"];
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
