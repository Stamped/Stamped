//
//  STSimpleImageList.m
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleImageList.h"
#import "STSimpleImage.h"
#import "STSimpleAction.h"

@implementation STSimpleImageList

@synthesize sizes = sizes_;
@synthesize caption = caption_;
@synthesize action = action_;

- (id)initWithCoder:(NSCoder *)decoder
{
  self = [super init];
  if (self) {
    sizes_ = [[decoder decodeObjectForKey:@"sizes"] retain];
    caption_ = [[decoder decodeObjectForKey:@"caption"] retain];
    action_ = [[decoder decodeObjectForKey:@"action"] retain];
  }
  return self;
}

- (void)dealloc
{
  [sizes_ release];
  [caption_ release];
  [action_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.sizes forKey:@"sizes"];
  [encoder encodeObject:self.caption forKey:@"caption"];
  [encoder encodeObject:self.action forKey:@"action"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleImageList class]];
  
  [mapping mapAttributes:
   @"caption",
   nil];
  
  [mapping mapRelationship:@"sizes" withMapping:[STSimpleImage mapping]];
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  return mapping;
}

@end
