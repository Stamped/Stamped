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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _name = [[decoder decodeObjectForKey:@"name"] retain];
    _bio = [[decoder decodeObjectForKey:@"bio"] retain];
    _website = [[decoder decodeObjectForKey:@"website"] retain];
    _location = [[decoder decodeObjectForKey:@"location"] retain];
    _identifier = [[decoder decodeObjectForKey:@"identifier"] retain];
    
    _numStamps = [[decoder decodeObjectForKey:@"numStamps"] retain];
    _numStampsLeft = [[decoder decodeObjectForKey:@"numStampsLeft"] retain];
    _numFriends = [[decoder decodeObjectForKey:@"numFriends"] retain];
    _numFollowers = [[decoder decodeObjectForKey:@"numFollowers"] retain];
    _numTodos = [[decoder decodeObjectForKey:@"numTodos"] retain];
    _numCredits = [[decoder decodeObjectForKey:@"numCredits"] retain];
    _numCreditsGiven = [[decoder decodeObjectForKey:@"numCreditsGiven"] retain];
    _numLikes = [[decoder decodeObjectForKey:@"numLikes"] retain];
    _numLikesGiven = [[decoder decodeObjectForKey:@"numLikesGiven"] retain];
    
    _distribution = [[decoder decodeObjectForKey:@"distribution"] retain];
  }
  return self;
}

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

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.bio forKey:@"bio"];
  [encoder encodeObject:self.website forKey:@"website"];
  [encoder encodeObject:self.location forKey:@"location"];
  [encoder encodeObject:self.identifier forKey:@"identifier"];
  
  [encoder encodeObject:self.numStamps forKey:@"numStamps"];
  [encoder encodeObject:self.numStampsLeft forKey:@"numStampsLeft"];
  [encoder encodeObject:self.numFriends forKey:@"numFriends"];
  [encoder encodeObject:self.numFollowers forKey:@"numFollowers"];
  [encoder encodeObject:self.numTodos forKey:@"numTodos"];
  [encoder encodeObject:self.numCredits forKey:@"numCredits"];
  [encoder encodeObject:self.numCreditsGiven forKey:@"numCreditsGiven"];
  [encoder encodeObject:self.numLikes forKey:@"numLikes"];
  [encoder encodeObject:self.numLikesGiven forKey:@"numLikesGiven"];
  
  [encoder encodeObject:self.distribution forKey:@"distribution"];
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
