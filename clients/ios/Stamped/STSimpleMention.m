//
//  STSimpleMention.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMention.h"

@implementation STSimpleMention

@synthesize screenName = _screenName;
@synthesize userID = _userID;
@synthesize indices = _indices;

- (void)dealloc
{
  [_screenName release];
  [_userID release];
  [_indices release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMention class]];
  
  [mapping mapKeyPathsToAttributes:
   @"screen_name", @"screenName",
   @"user_id", @"userID",
   nil];
  
  [mapping mapAttributes:
   @"indices",
   nil];
  
  return mapping;
}

@end
