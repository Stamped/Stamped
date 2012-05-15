//
//  STSimpleActivityCount.m
//  Stamped
//
//  Created by Landon Judkins on 5/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivityCount.h"

@implementation STSimpleActivityCount

@synthesize numberUnread = numberUnread_;

- (id)initWithCoder:(NSCoder *)decoder
{
  self = [super init];
  if (self) {
    numberUnread_ = [[decoder decodeObjectForKey:@"numberUnread"] retain];
  }
  return self;
}

- (void)dealloc
{
  [numberUnread_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.numberUnread forKey:@"numberUnread"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivityCount class]];
  
  [mapping mapKeyPathsToAttributes: 
   @"num_unread", @"numberUnread",
   nil];
  
  return mapping;
}

@end
