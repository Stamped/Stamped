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

- (void)dealloc
{
  [_genre release];
  [_userID release];
  [super dealloc];
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
