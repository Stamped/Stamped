//
//  STSimpleHours.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleHours.h"

@implementation STSimpleHours

@synthesize open = _open;
@synthesize close = _close;
@synthesize desc = _desc;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _open = [[decoder decodeObjectForKey:@"open"] retain];
    _close = [[decoder decodeObjectForKey:@"close"] retain];
    _desc = [[decoder decodeObjectForKey:@"desc"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_open release];
  [_close release];
  [_desc release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.open forKey:@"open"];
  [encoder encodeObject:self.close forKey:@"close"];
  [encoder encodeObject:self.desc forKey:@"desc"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleHours class]];
  
  [mapping mapAttributes:
   @"open",
   @"close",
   @"desc",
   nil];
  
  return mapping;
}

@end
