//
//  STSimpleUser.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleUser.h"

@implementation STSimpleUser

@synthesize userID = _userID;
@synthesize screenName = _screenName;
@synthesize colorPrimary = _colorPrimary;
@synthesize colorSecondary = _colorSecondary;
@synthesize privacy = _privacy;
@synthesize imageURL = _imageURL;

- (void)dealloc
{
  [_userID release];
  [_screenName release];
  [_colorPrimary release];
  [_colorSecondary release];
  [_privacy release];
  [_imageURL release];
  [super dealloc];
}


+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleUser class]];
  
  [mapping mapKeyPathsToAttributes:
   @"user_id", @"userID",
   @"screen_name", @"screenName",
   @"color_primary", @"colorPrimary",
   @"color_secondary", @"colorSecondary",
   @"image_url", @"imageURL",
   nil];
  
  [mapping mapAttributes:
   @"privacy",
   nil];
  
  return mapping;
}


@end
