//
//  DetailedEntity.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/26/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "DetailedEntity.h"


@implementation DetailedEntity

@dynamic address;
@dynamic albums;
@dynamic amazonURL;
@dynamic artist;
@dynamic author;
@dynamic cast;
@dynamic category;
@dynamic city;
@dynamic coordinates;
@dynamic cuisine;
@dynamic desc;
@dynamic director;
@dynamic entityID;
@dynamic fandangoURL;
@dynamic format;
@dynamic genre;
@dynamic hours;
@dynamic image;
@dynamic inTheaters;
@dynamic isbn;
@dynamic itunesShortURL;
@dynamic itunesURL;
@dynamic label;
@dynamic language;
@dynamic length;
@dynamic location;
@dynamic mostRecentStampDate;
@dynamic neighborhood;
@dynamic openTableURL;
@dynamic phone;
@dynamic price;
@dynamic publisher;
@dynamic rating;
@dynamic releaseDate;
@dynamic songs;
@dynamic state;
@dynamic street;
@dynamic subcategory;
@dynamic substreet;
@dynamic subtitle;
@dynamic title;
@dynamic website;
@dynamic year;
@dynamic zipcode;

- (UIImage*)categoryImage {
  if (self.category)
    return [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[self.category lowercaseString]]];
  
  return [UIImage imageNamed:@"cat_icon_other"];
}

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

@end
