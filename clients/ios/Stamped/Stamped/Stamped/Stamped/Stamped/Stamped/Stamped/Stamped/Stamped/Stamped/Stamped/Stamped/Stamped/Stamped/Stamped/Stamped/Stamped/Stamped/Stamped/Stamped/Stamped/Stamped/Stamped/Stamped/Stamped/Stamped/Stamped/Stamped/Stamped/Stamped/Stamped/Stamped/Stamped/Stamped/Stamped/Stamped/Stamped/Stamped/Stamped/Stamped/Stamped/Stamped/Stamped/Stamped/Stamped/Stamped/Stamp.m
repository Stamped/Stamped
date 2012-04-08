//
//  Stamp.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Stamp.h"
#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "User.h"


@implementation Stamp

@dynamic blurb;
@dynamic created;
@dynamic deleted;
@dynamic imageDimensions;
@dynamic imageURL;
@dynamic isFavorited;
@dynamic isLiked;
@dynamic modified;
@dynamic numComments;
@dynamic numLikes;
@dynamic stampID;
@dynamic URL;
@dynamic comments;
@dynamic credits;
@dynamic entityObject;
@dynamic events;
@dynamic favorites;
@dynamic user;
@dynamic via;

- (NSString*)entityID {
  if (self.entityObject) {
    return self.entityObject.entityID;
  }
  else {
    return nil;
  }
}

- (NSString*)userID {
  if (self.user) {
    return self.user.userID;
  }
  else {
    return nil;
  }
}

@end
