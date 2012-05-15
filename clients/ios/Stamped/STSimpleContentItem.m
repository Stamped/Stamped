//
//  STSimpleContentItem.m
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleContentItem.h"
#import "STSimpleImageList.h"

@implementation STSimpleContentItem

@synthesize modified = modified_;
@synthesize blurb = blurb_;
@synthesize created = created_;
@synthesize images = images_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    modified_ = [[decoder decodeObjectForKey:@"modified"] retain];
    blurb_ = [[decoder decodeObjectForKey:@"blurb"] retain];
    created_ = [[decoder decodeObjectForKey:@"created"] retain];
    images_ = [[decoder decodeObjectForKey:@"images"] retain];
  }
  return self;
}

- (void)dealloc
{
  [modified_ release];
  [blurb_ release];
  [created_ release];
  [images_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.modified forKey:@"modified"];
  [encoder encodeObject:self.blurb forKey:@"blurb"];
  [encoder encodeObject:self.created forKey:@"created"];
  [encoder encodeObject:self.images forKey:@"images"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleContentItem class]];
  
  [mapping mapAttributes:
   @"modified",
   @"blurb",
   @"created",
   nil];
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  
  return mapping;
}

@end
