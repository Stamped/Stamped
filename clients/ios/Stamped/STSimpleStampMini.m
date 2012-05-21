//
//  STSimpleStampMini.m
//  Stamped
//
//  Created by Landon Judkins on 5/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampMini.h"

@implementation STSimpleStampMini

@synthesize stampID = _stampID;
@synthesize created = _created;
@synthesize modified = _modified;
@synthesize stamped = _stamped;
@synthesize updated = _updated;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _stampID = [[decoder decodeObjectForKey:@"stampID"] retain];
    _created = [[decoder decodeObjectForKey:@"created"] retain];
    _modified = [[decoder decodeObjectForKey:@"modified"] retain];
    _stamped = [[decoder decodeObjectForKey:@"stamped"] retain];
    _updated = [[decoder decodeObjectForKey:@"updated"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_stampID release];
  [_created release];
  [_modified release];
  [_stamped release];
  [_updated release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.stampID forKey:@"stampID"];
  [encoder encodeObject:self.created forKey:@"created"];
  [encoder encodeObject:self.modified forKey:@"modified"];
  [encoder encodeObject:self.stamped forKey:@"stamped"];
  [encoder encodeObject:self.updated forKey:@"updated"];
}

@end
