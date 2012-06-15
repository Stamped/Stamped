//
//  STSimpleComment.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleComment.h"
#import "STSimpleUser.h"

@implementation STSimpleComment

@synthesize blurb = _blurb;
@synthesize commentID = _commentID;
@synthesize stampID = _stampID;
@synthesize created = _created;
@synthesize user = _user;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _blurb = [[decoder decodeObjectForKey:@"blurb"] retain];
    _commentID = [[decoder decodeObjectForKey:@"commentID"] retain];
    _stampID = [[decoder decodeObjectForKey:@"stampID"] retain];
    _created = [[decoder decodeObjectForKey:@"created"] retain];
    _user = [[decoder decodeObjectForKey:@"user"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_blurb release];
  [_commentID release];
  [_stampID release];
  [_created release];
  [_user release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.blurb forKey:@"blurb"];
  [encoder encodeObject:self.commentID forKey:@"commentID"];
  [encoder encodeObject:self.stampID forKey:@"stampID"];
  [encoder encodeObject:self.created forKey:@"created"];
  [encoder encodeObject:self.user forKey:@"user"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleComment class]];
  
  [mapping mapKeyPathsToAttributes:
   @"comment_id",@"commentID",
   @"stamp_id",@"stampID",
   nil];
  
  [mapping mapAttributes:
   @"blurb",
   @"created",
   nil];
  
  [mapping mapRelationship:@"user" withMapping:[STSimpleUser mapping]];
  
  return mapping;
}


@end
