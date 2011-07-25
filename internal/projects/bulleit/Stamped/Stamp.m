//
//  Stamp.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Stamp.h"
#import "User.h"
#import "Entity.h"

@implementation Stamp
@dynamic stampID;
@dynamic blurb;
@dynamic numComments;
@dynamic lastModified;
@dynamic user;
@dynamic entityObject;

- (StampCategory)category {
  NSString* cat = self.entityObject.category;
  if ([cat isEqualToString:@"Place"]) {
    return StampCategoryPlace;
  } else if ([cat isEqualToString:@"Film"]) {
    return StampCategoryFilm;
  } else if ([cat isEqualToString:@"Music"]) {
    return StampCategoryMusic;
  } else if ([cat isEqualToString:@"Book"]) {
    return StampCategoryBook;
  }
  return StampCategoryOther;
}

@end
