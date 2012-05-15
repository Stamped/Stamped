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
#import "STStampedAPI.h"

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

+ (STSimpleStamp*)augmentedStampWithStamp:(id<STStamp>)stamp
                                     todo:(id<STUser>)todo
                                     like:(id<STUser>)like
                                  comment:(id<STComment>)comment
                                andCredit:(id<STStamp>)credit {
  STSimpleStamp* copy = [STSimpleStamp stampWithStamp:stamp];
  STSimplePreviews* previews;
  if (stamp.previews) {
    previews = [STSimplePreviews previewsWithPreviews:stamp.previews];
  }
  else {
    previews = [[[STSimplePreviews alloc] init] autorelease];
  }
  if (todo) {
    NSMutableArray<STUser>* todos;
    if (previews.todos) {
      todos = [NSMutableArray arrayWithArray:previews.todos];
    }
    else {
      todos = [NSMutableArray array];
    }
    [todos insertObject:todo atIndex:0];
    if ([todo.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
      copy.isTodod = [NSNumber numberWithBool:YES];
    }
    previews.todos = todos;
  }
  if (like) {
    NSMutableArray<STUser>* likes;
    if (previews.likes) {
      likes = [NSMutableArray arrayWithArray:previews.likes];
    }
    else {
      likes = [NSMutableArray array];
    }
    [likes insertObject:like atIndex:0];
    previews.likes = likes;
    if ([like.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
      copy.isLiked = [NSNumber numberWithBool:YES];
    }
    copy.numLikes = [NSNumber numberWithInteger:copy.numLikes.integerValue + 1];
  }
  if (comment) {
    NSMutableArray<STComment>* comments;
    if (previews.comments) {
      comments = [NSMutableArray arrayWithArray:previews.comments];
    }
    else {
      comments = [NSMutableArray array];
    }
    [comments insertObject:comment atIndex:0];
    copy.numComments = [NSNumber numberWithInteger:copy.numComments.integerValue + 1];
    previews.comments = comments;
  }
  if (credit) {
    NSMutableArray<STStamp>* credits;
    if (previews.credits) {
      credits = [NSMutableArray arrayWithArray:previews.credits];
    }
    else {
      credits = [NSMutableArray array];
    }
    STSimpleStamp* previewlessStamp = [STSimpleStamp stampWithStamp:credit];
    previewlessStamp.previews = nil;
    [credits insertObject:previewlessStamp atIndex:0];
    previews.credits = credits;
  }
  copy.previews = previews;
  copy.modified = [NSDate date];
  return copy;
}

+ (STSimpleStamp*)reducedStampWithStamp:(id<STStamp>)stamp 
                                   todo:(id<STUser>)todo
                                   like:(id<STUser>)like
                                comment:(id<STComment>)comment
                              andCredit:(id<STStamp>)credit {
  BOOL modified = NO;
  STSimpleStamp* copy = [STSimpleStamp stampWithStamp:stamp];
  if (stamp.previews) {
    STSimplePreviews* previews = [STSimplePreviews previewsWithPreviews:stamp.previews];
    if (todo) {
      if (previews.todos) {
        NSMutableArray<STUser>* todos = [NSMutableArray arrayWithArray:previews.todos];
        id<STUser> target = nil;
        for (id<STUser> cur in todos) {
          if ([cur.userID isEqualToString:todo.userID]) {
            target = cur;
          }
        }
        if (target) {
          [todos removeObject:target];
          if ([todo.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
            copy.isTodod = [NSNumber numberWithBool:NO];
          }
          previews.todos = todos;
          modified = YES;
        }
      }
    }
    if (like) {
      if (previews.likes) {
        NSMutableArray<STUser>* likes = [NSMutableArray arrayWithArray:previews.likes];
        id<STUser> target = nil;
        for (id<STUser> cur in likes) {
          if ([cur.userID isEqualToString:like.userID]) {
            target = cur;
          }
        }
        if (target) {
          [likes removeObject:target];
          if (copy.numLikes.integerValue > 0) {
            copy.numLikes = [NSNumber numberWithInteger:copy.numLikes.integerValue - 1];
          }
          if ([like.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
            copy.isLiked = [NSNumber numberWithBool:NO];
          }
          previews.likes = likes;
          modified = YES;
        }
      }
    }
    if (comment) {
      if (previews.comments) {
        NSMutableArray<STComment>* comments = [NSMutableArray arrayWithArray:previews.comments];
        id<STComment> target = nil;
        for (id<STComment> cur in comments) {
          if ([cur.commentID isEqualToString:comment.commentID]) {
            target = cur;
          }
        }
        if (target) {
          [comments removeObject:target];
          if (copy.numComments.integerValue > 0) {
            copy.numComments = [NSNumber numberWithInteger:copy.numComments.integerValue - 1];
          }
          previews.comments = comments;
          modified = YES;
        }
      }
    }
    if (credit) {
      if (previews.credits) {
        NSMutableArray<STStamp>* credits = [NSMutableArray arrayWithArray:previews.credits];
        id<STStamp> target = nil;
        for (id<STStamp> cur in credits) {
          if ([cur.stampID isEqualToString:credit.stampID]) {
            target = cur;
            break;
          }
        }
        if (target) {
          [credits removeObject:target];
          previews.credits = credits;
          modified = YES;
        }
      }
    }
    if (modified) {
      copy.previews = previews;
      copy.modified = [NSDate date];
    }
    return copy;
  }
  else {
    return copy;
  }
}

@end
