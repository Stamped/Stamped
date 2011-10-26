//
//  Entity.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <CoreLocation/CoreLocation.h>

#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "Stamp.h"

@implementation Entity

@dynamic category;
@dynamic coordinates;
@dynamic entityID;
@dynamic mostRecentStampDate;
@dynamic subcategory;
@dynamic subtitle;
@dynamic title;
@dynamic events;
@dynamic favorite;
@dynamic stamps;

- (UIImage*)categoryImage {
  if (self.category)
    return [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[self.category lowercaseString]]];
  
  return [UIImage imageNamed:@"cat_icon_other"];
}

- (EntityCategory)entityCategory {
  NSString* cat = self.category;
  if ([cat isEqualToString:@"food"]) {
    return EntityCategoryFood;
  } else if ([cat isEqualToString:@"film"]) {
    return EntityCategoryFilm;
  } else if ([cat isEqualToString:@"music"]) {
    return EntityCategoryMusic;
  } else if ([cat isEqualToString:@"book"]) {
    return EntityCategoryBook;
  }
  return EntityCategoryOther;
}

- (id)valueForUndefinedKey:(NSString*)key {
  return nil;
}

@end
