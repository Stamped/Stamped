//
//  STSimpleCredit.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleCredit.h"

@implementation STSimpleCredit 

@synthesize userID = _userID;
@synthesize screenName = _screenName;
@synthesize stampID = _stampID;
@synthesize colorPrimary = _colorPrimary;
@synthesize colorSecondary = _colorSecondary;
@synthesize privacy = _privacy;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _userID = [[decoder decodeObjectForKey:@"userID"] retain];
    _screenName = [[decoder decodeObjectForKey:@"screenName"] retain];
    _stampID = [[decoder decodeObjectForKey:@"stampID"] retain];
    _colorPrimary = [[decoder decodeObjectForKey:@"colorPrimary"] retain];
    _colorSecondary = [[decoder decodeObjectForKey:@"colorSecondary"] retain];
    _privacy = [[decoder decodeObjectForKey:@"privacy"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_userID release];
  [_screenName release];
  [_stampID release];
  [_colorPrimary release];
  [_colorSecondary release];
  [_privacy release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.userID forKey:@"userID"];
  [encoder encodeObject:self.screenName forKey:@"screenName"];
  [encoder encodeObject:self.stampID forKey:@"stampID"];
  [encoder encodeObject:self.colorPrimary forKey:@"colorPrimary"];
  [encoder encodeObject:self.colorSecondary forKey:@"colorSecondary"];
  [encoder encodeObject:self.privacy forKey:@"privacy"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleCredit class]];
  
  [mapping mapKeyPathsToAttributes:
   @"user_id", @"userID",
   @"screen_name", @"screenName",
   @"stamp_id", @"stampID",
   @"color_primary", @"colorPrimary",
   @"color_secondary", @"colorSecondary",
   nil];
  
  [mapping mapAttributes:
   @"privacy",
   nil];
  
  return mapping;
}

@end
