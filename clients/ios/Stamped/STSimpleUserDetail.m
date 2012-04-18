//
//  STSimpleUserDetail.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleUserDetail.h"
#import "STSimpleDistributionItem.h"

@implementation STSimpleUserDetail

@synthesize name = _name;
@synthesize bio = _bio;
@synthesize website = _website;
@synthesize location = _location;
@synthesize identifier = _identifier;

@synthesize numStamps = _numStamps;
@synthesize numStampsLeft = _numStampsLeft;
@synthesize numFriends = _numFriends;
@synthesize numFollowers = _numFollowers;
@synthesize numTodos = _numTodos;
@synthesize numCredits = _numCredits;
@synthesize numCreditsGiven = _numCreditsGiven;
@synthesize numLikes = _numLikes;
@synthesize numLikesGiven = _numLikesGiven;

@synthesize distribution = _distribution;

- (void)dealloc
{
  [_name release];
  [_bio release];
  [_website release];
  [_location release];
  [_identifier release];
  
  [_numStamps release];
  [_numStampsLeft release];
  [_numFriends release];
  [_numFollowers release];
  [_numTodos release];
  [_numCredits release];
  [_numCreditsGiven release];
  [_numLikes release];
  [_numLikesGiven release];
  
  [_distribution release];
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleUserDetail class]];
  
  [mapping mapKeyPathsToAttributes:
   //From STSimpleUser.m
   @"user_id", @"userID",
   @"screen_name", @"screenName",
   @"color_primary", @"primaryColor",
   @"color_secondary", @"secondaryColor",
   @"image_url", @"imageURL",
   //From UserDetail
   @"num_stamps", @"numStamps",
   @"num_stamps_left", @"numStampsLeft",
   @"num_friends", @"numFriends",
   @"num_followers", @"numFollowers",
   @"num_faves", @"numTodos",
   @"num_credits", @"numCredits",
   @"num_credits_given", @"numCreditsGiven",
   @"num_likes", @"numLikes",
   @"num_likes_given", @"numLikesGiven",
   nil];
  
  [mapping mapAttributes:
  //From User
   @"privacy",
   //From UserDetail
   @"name",
   @"bio",
   @"website",
   @"location",
   @"identifier",
   nil];
  
  [mapping mapRelationship:@"distribution" withMapping:[STSimpleDistributionItem mapping]];
  
  return mapping;
}

@end
