//
//  Stamp.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/26/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Stamp.h"
#import "Comment.h"
#import "Entity.h"
#import "User.h"

NSString* kStampDidChangeNotification = @"StampDidChangeNotification";

@implementation Stamp

@dynamic blurb;
@dynamic created;
@dynamic numComments;
@dynamic stampID;
@dynamic entityObject;
@dynamic user;
@dynamic comments;

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
