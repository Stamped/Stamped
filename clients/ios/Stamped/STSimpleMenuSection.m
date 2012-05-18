//
//  STSimpleMenuSection.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenuSection.h"
#import "STSimpleMenuItem.h"

@implementation STSimpleMenuSection

@synthesize title = _title;
@synthesize desc = _desc;
@synthesize shortDesc = _shortDesc;
@synthesize items = _items;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _title = [[decoder decodeObjectForKey:@"title"] retain];
    _desc = [[decoder decodeObjectForKey:@"desc"] retain];
    _shortDesc = [[decoder decodeObjectForKey:@"shortDesc"] retain];
    _items = [[decoder decodeObjectForKey:@"items"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_title release];
  [_desc release];
  [_shortDesc release];
  [_items release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.title forKey:@"title"];
  [encoder encodeObject:self.desc forKey:@"desc"];
  [encoder encodeObject:self.shortDesc forKey:@"shortDesc"];
  [encoder encodeObject:self.items forKey:@"items"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenuSection class]];
  
  [mapping mapKeyPathsToAttributes:
   @"short_desc", @"shortDesc",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"desc",
   nil];
  
  [mapping mapRelationship:@"items" withMapping:[STSimpleMenuItem mapping]];
  
  return mapping;
}

@end
