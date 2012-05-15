//
//  STSimpleBadge.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleBadge.h"

@implementation STSimpleBadge

@synthesize genre = _genre;
@synthesize userID = _userID;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _genre = [[decoder decodeObjectForKey:@"genre"] retain];
    _userID = [[decoder decodeObjectForKey:@"userID"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_genre release];
  [_userID release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.genre forKey:@"genre"];
  [encoder encodeObject:self.userID forKey:@"userID"];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleBadge class]];
  
  [mapping mapKeyPathsToAttributes:
   @"user_id", @"userID",
   nil];
  
  [mapping mapAttributes:
   @"genre",
   nil];
  
  return mapping;
}

@end
