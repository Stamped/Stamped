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
#import "STSimpleContentItem.h"
#import "STSimplePreviews.h"

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
@synthesize previews = previews_;
@synthesize mentions = _mentions;
@synthesize credits = _credits;
@synthesize badges = _badges;
@synthesize contents = contents_;

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
  [previews_ release];
  [_mentions release];
  [_credits release];
  [_badges release];
  [contents_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [STSimpleStamp mappingWithoutPreview];
  [mapping mapRelationship:@"previews" withMapping:[STSimplePreviews mapping]];
  return mapping;
}

+ (RKObjectMapping*)mappingWithoutPreview {
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
  [mapping mapRelationship:@"mentions" withMapping:[STSimpleMention mapping]];
  [mapping mapKeyPath:@"credit" toRelationship:@"credits" withMapping:[STSimpleCredit mapping]];
  [mapping mapRelationship:@"badges" withMapping:[STSimpleBadge mapping]];
  [mapping mapRelationship:@"contents" withMapping:[STSimpleContentItem mapping]];
  return mapping;
}

+ (STSimpleStamp*)stampWithStamp:(id<STStamp>)stamp {
  STSimpleStamp* copy = [[[STSimpleStamp alloc] init] autorelease];
  copy.blurb = stamp.blurb;
  copy.created = stamp.created;
  copy.deleted = stamp.deleted;
  copy.imageDimensions = stamp.imageDimensions;
  copy.imageURL = stamp.imageURL;
  copy.isTodod = stamp.isTodod;
  copy.isLiked = stamp.isLiked;
  copy.modified = stamp.modified;
  copy.numComments = stamp.numComments;
  copy.numLikes = stamp.numLikes;
  copy.stampID = stamp.stampID;
  copy.URL = stamp.URL;
  copy.via = stamp.via;
  copy.entity = stamp.entity;
  copy.user = stamp.user;
  copy.previews = stamp.previews;
  copy.mentions = stamp.mentions;
  copy.credits = stamp.credits;
  copy.badges = stamp.badges;
  copy.contents = stamp.contents;
  return copy;
}

@end
