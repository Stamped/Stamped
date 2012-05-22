//
//  STSimpleMetadataItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMetadataItem.h"
#import "STSimpleAction.h"

@implementation STSimpleMetadataItem

@synthesize name = name_;
@synthesize value = value_;
@synthesize icon = icon_;
@synthesize link = link_;
@synthesize action = action_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    value_ = [[decoder decodeObjectForKey:@"value"] retain];
    icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
    link_ = [[decoder decodeObjectForKey:@"link"] retain];
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
  }
  return self;
}

- (void)dealloc {
  self.name = nil;
  self.value = nil;
  self.icon = nil;
  self.link = nil;
  self.action = nil;
  
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.value forKey:@"value"];
  [encoder encodeObject:self.icon forKey:@"icon"];
  [encoder encodeObject:self.link forKey:@"link"];
  [encoder encodeObject:self.action forKey:@"action"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMetadataItem class]];
  
  [mapping mapAttributes:
   @"name",
   @"value",
   @"icon",
   @"link",
   nil];
  
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
