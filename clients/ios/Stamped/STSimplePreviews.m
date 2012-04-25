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

@implementation STSimplePreviews

@synthesize comments = comments_;
@synthesize likes = likes_;
@synthesize todos = todos_;

- (void)dealloc
{
  [comments_ release];
  [likes_ release];
  [todos_ release];
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePreviews class]];
  
  [mapping mapRelationship:@"comments" withMapping:[STSimpleComment mapping]];
  [mapping mapRelationship:@"likes" withMapping:[STSimpleUser mapping]];
  [mapping mapRelationship:@"todos" withMapping:[STSimpleUser mapping]];
  
  return mapping;
}

@end
