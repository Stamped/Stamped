//
//  STSimpleImage.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleImage.h"

@implementation STSimpleImage

@synthesize url = _url;
@synthesize width = _width;
@synthesize height = _height;
@synthesize source = _source;
@synthesize filter = _filter;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _url = [[decoder decodeObjectForKey:@"url"] retain];
    _width = [[decoder decodeObjectForKey:@"width"] retain];
    _height = [[decoder decodeObjectForKey:@"height"] retain];
    _source = [[decoder decodeObjectForKey:@"source"] retain];
    _filter = [[decoder decodeObjectForKey:@"filter"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_url release];
  [_width release];
  [_height release];
  [_source release];
  [_filter release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.url forKey:@"url"];
  [encoder encodeObject:self.width forKey:@"width"];
  [encoder encodeObject:self.height forKey:@"height"];
  [encoder encodeObject:self.source forKey:@"source"];
  [encoder encodeObject:self.filter forKey:@"filter"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleImage class]];
  
  [mapping mapAttributes:
   @"url",
   @"width",
   @"height",
   @"source",
   @"filter",
   nil];
  
  return mapping;
}

@end
