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
@synthesize primaryColor = _primaryColor;
@synthesize secondaryColor = _secondaryColor;
@synthesize privacy = _privacy;
@synthesize imageURL = _imageURL;

- (void)dealloc
{
  [_userID release];
  [_screenName release];
  [_primaryColor release];
  [_secondaryColor release];
  [_privacy release];
  [_imageURL release];
  [super dealloc];
}


+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleUser class]];
  
  [mapping mapKeyPathsToAttributes:
   @"user_id", @"userID",
   @"screen_name", @"screenName",
   @"color_primary", @"primaryColor",
   @"color_secondary", @"secondaryColor",
   @"image_url", @"imageURL",
   nil];
  
  [mapping mapAttributes:
   @"privacy",
   nil];
  
  return mapping;
}

+ (STSimpleUser*)userFromLegacyUser:(User*)legacyUser {
  STSimpleUser* user = [[STSimpleUser alloc] init];
  user.userID = legacyUser.userID;
  user.screenName = legacyUser.screenName;
  user.primaryColor = legacyUser.primaryColor;
  user.secondaryColor = legacyUser.secondaryColor;
  user.imageURL = legacyUser.imageURL;
  return user;
}


@end
