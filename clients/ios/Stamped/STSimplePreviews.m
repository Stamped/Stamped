//
//  STSimplePreviews.m
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePreviews.h"
#import "STSimpleUser.h"
#import "STSimpleComment.h"
#import "STSimpleStamp.h"

@implementation STSimplePreviews

@synthesize comments = comments_;
@synthesize likes = likes_;
@synthesize todos = todos_;
@synthesize credits = credits_;

- (void)dealloc
{
  [comments_ release];
  [likes_ release];
  [todos_ release];
  [credits_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePreviews class]];
  
  [mapping mapRelationship:@"comments" withMapping:[STSimpleComment mapping]];
  [mapping mapRelationship:@"likes" withMapping:[STSimpleUser mapping]];
  [mapping mapRelationship:@"todos" withMapping:[STSimpleUser mapping]];
  [mapping mapRelationship:@"credits" withMapping:[STSimpleStamp mappingWithoutPreview]];
  
  return mapping;
}

+ (STSimplePreviews*)previewsWithPreviews:(id<STPreviews>)previews {
  STSimplePreviews* copy = [[[STSimplePreviews alloc] init] autorelease];
  copy.comments = previews.comments;
  copy.likes = previews.likes;
  copy.todos = previews.todos;
  copy.credits = previews.credits;
  return copy;
}

@end
