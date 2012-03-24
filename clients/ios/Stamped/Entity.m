//
//  Entity.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <CoreLocation/CoreLocation.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "Stamp.h"
#import "User.h"

@implementation Entity

@dynamic category;
@dynamic coordinates;
@dynamic entityID;
@dynamic localModificationDate;
@dynamic mostRecentStampDate;
@dynamic subcategory;
@dynamic subtitle;
@dynamic title;
@dynamic events;
@dynamic favorite;
@dynamic stamps;

- (UIImage*)inboxTodoCategoryImage {
  if (self.category)
    return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_inbox-todo_%@", self.category.lowercaseString]];
  
  return [UIImage imageNamed:@"cat_icon_inbox-todo_other"];
}

- (UIImage*)highlightedInboxTodoCategoryImage {
  if (self.category)
    return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_inbox-todo_%@_white", self.category.lowercaseString]];
  
  return [UIImage imageNamed:@"cat_icon_inbox-todo_other_white"];
}

- (UIImage*)stampDetailCategoryImage {
  if (self.category)
    return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_sDetail_%@", self.category.lowercaseString]];
  
  return [UIImage imageNamed:@"cat_icon_sDetail_other"];
}

- (UIImage*)entitySearchCategoryImage {
  if (self.category)
    return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_eSearch_%@", self.category.lowercaseString]];
  
  return [UIImage imageNamed:@"cat_icon_eSearch_other"];
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

- (void)updateLatestStamp {
  User* currentUser = [AccountManager sharedManager].currentUser;
  NSSet* following = currentUser.following;
  if (!following)
    following = [NSSet set];
  
        
  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
  NSArray* filteredStamps = [[self.stamps allObjects] filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"(user IN %@ OR user.userID == %@) AND deleted == NO", following, currentUser.userID]];
  if (filteredStamps.count == 0)
    return;

  filteredStamps = [filteredStamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  Stamp* latestStamp = [filteredStamps objectAtIndex:0];
  self.mostRecentStampDate = latestStamp.created;
}

@end
