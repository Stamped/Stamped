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

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    comments_ = [[decoder decodeObjectForKey:@"comments"] retain];
    likes_ = [[decoder decodeObjectForKey:@"likes"] retain];
    todos_ = [[decoder decodeObjectForKey:@"todos"] retain];
    credits_ = [[decoder decodeObjectForKey:@"credits"] retain];
  }
  return self;
}

- (void)dealloc
{
  [comments_ release];
  [likes_ release];
  [todos_ release];
  [credits_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.comments forKey:@"comments"];
  [encoder encodeObject:self.likes forKey:@"likes"];
  [encoder encodeObject:self.todos forKey:@"todos"];
  [encoder encodeObject:self.credits forKey:@"credits"];
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
