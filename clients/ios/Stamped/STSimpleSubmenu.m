//
//  STSimpleSubmenu.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleSubmenu.h"
#import "STSimpleTimes.h"
#import "STSimpleMenuSection.h"

@implementation STSimpleSubmenu

@synthesize title = _title;
@synthesize times = _times;
@synthesize footnote = _footnote;
@synthesize desc = _desc;
@synthesize shortDesc = _shortDesc;
@synthesize sections = _sections;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _title = [[decoder decodeObjectForKey:@"title"] retain];
    _times = [[decoder decodeObjectForKey:@"times"] retain];
    _footnote = [[decoder decodeObjectForKey:@"footnote"] retain];
    _desc = [[decoder decodeObjectForKey:@"desc"] retain];
    _shortDesc = [[decoder decodeObjectForKey:@"shortDesc"] retain];
    _sections = [[decoder decodeObjectForKey:@"sections"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_title release];
  [_times release];
  [_footnote release];
  [_desc release];
  [_shortDesc release];
  [_sections release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.title forKey:@"title"];
  [encoder encodeObject:self.times forKey:@"times"];
  [encoder encodeObject:self.footnote forKey:@"footnote"];
  [encoder encodeObject:self.desc forKey:@"desc"];
  [encoder encodeObject:self.shortDesc forKey:@"shortDesc"];
  [encoder encodeObject:self.sections forKey:@"sections"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleSubmenu class]];
  
  [mapping mapKeyPathsToAttributes:
   @"short_desc", @"shortDesc",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"footnote",
   @"desc",
   nil];
  
  [mapping mapRelationship:@"times" withMapping:[STSimpleTimes mapping]];
  [mapping mapRelationship:@"sections" withMapping:[STSimpleMenuSection mapping]];
  
  return mapping;
}

@end
