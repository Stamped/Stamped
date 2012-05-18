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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _screenName = [[decoder decodeObjectForKey:@"screenName"] retain];
    _userID = [[decoder decodeObjectForKey:@"userID"] retain];
    _indices = [[decoder decodeObjectForKey:@"indices"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_screenName release];
  [_userID release];
  [_indices release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.screenName forKey:@"screenName"];
  [encoder encodeObject:self.userID forKey:@"userID"];
  [encoder encodeObject:self.indices forKey:@"indices"];
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
