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
