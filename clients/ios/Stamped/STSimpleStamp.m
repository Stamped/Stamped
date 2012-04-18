//
//  STSimpleStamp.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStamp.h"
#import "STSimpleEntity.h"
#import "STSimpleUser.h"
#import "STSimpleComment.h"
#import "STSimpleCredit.h"
#import "STSimpleMention.h"
#import "STSimpleBadge.h"

@implementation STSimpleStamp

@synthesize blurb = _blurb;
@synthesize created = _created;
@synthesize deleted = _deleted;
@synthesize imageDimensions = _imageDimensions;
@synthesize imageURL = _imageURL;
@synthesize isTodod = _isTodod;
@synthesize isLiked = _isLiked;
@synthesize modified = _modified;
@synthesize numComments = _numComments;
@synthesize numLikes = _numLikes;
@synthesize stampID = _stampID;
@synthesize URL = _URL;
@synthesize via = _via;

@synthesize entity = _entity;
@synthesize user = _user;
@synthesize commentsPreview = _commentsPreview;
@synthesize mentions = _mentions;
@synthesize credits = _credits;
@synthesize badges = _badges;

- (void)dealloc
{
  [_blurb release];
  [_created release];
  [_deleted release];
  [_imageDimensions release];
  [_imageURL release];
  [_isTodod release];
  [_isLiked release];
  [_modified release];
  [_numComments release];
  [_numLikes release];
  [_stampID release];
  [_URL release];
  [_via release];
  
  [_entity release];
  [_user release];
  [_commentsPreview release];
  [_mentions release];
  [_credits release];
  [_badges release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleStamp class]];
  
  [mapping mapKeyPathsToAttributes: 
   @"image_dimensions", @"imageDimensions",
   @"image_url", @"imageURL",
   @"is_liked", @"isLiked",
   @"is_fav", @"isTodod",
   @"stamp_id", @"stampID",
   @"url", @"URL",
   nil];
  
  [mapping mapAttributes:
   @"blurb",
   @"created",
   @"deleted",
   @"modified",
   @"via",
   nil];
  
  [mapping mapRelationship:@"entity" withMapping:[STSimpleEntity mapping]];
  [mapping mapRelationship:@"user" withMapping:[STSimpleUser mapping]];
  [mapping mapKeyPath:@"comment_preview" 
       toRelationship:@"commentsPreview" 
          withMapping:[STSimpleComment mapping]];
  [mapping mapRelationship:@"mentions" withMapping:[STSimpleMention mapping]];
  [mapping mapKeyPath:@"credit" toRelationship:@"credits" withMapping:[STSimpleCredit mapping]];
  [mapping mapRelationship:@"badges" withMapping:[STSimpleBadge mapping]];
  return mapping;
}

@end
