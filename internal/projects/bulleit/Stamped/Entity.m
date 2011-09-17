//
//  Entity.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Entity.h"
#import "Favorite.h"
#import "Stamp.h"

@implementation Entity

@dynamic address;
@dynamic street;
@dynamic substreet;
@dynamic city;
@dynamic state;
@dynamic zipcode;
@dynamic neighborhood;
@dynamic category;
@dynamic entityID;
@dynamic openTableURL;
@dynamic subtitle;
@dynamic title;
@dynamic coordinates;
@dynamic stamps;
@dynamic phone;
@dynamic favorite;
@dynamic subcategory;
@dynamic artist;
@dynamic desc;
@dynamic albums;
@dynamic songs;
@dynamic author;
@dynamic cast;
@dynamic director;
@dynamic year;
@dynamic hours;
@dynamic cuisine;
@dynamic price;
@dynamic website;
@dynamic itunesShortURL;
@dynamic itunesURL;
@dynamic releaseDate;
@dynamic genre;
@dynamic label;
@dynamic length;
@dynamic rating;
@dynamic format;
@dynamic publisher;
@dynamic isbn;
@dynamic language;
@dynamic amazonURL;
@dynamic inTheaters;
@dynamic fandangoURL;
@dynamic image;


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

- (NSString*)localizedPhoneNumber {
  if (![self.phone boolValue])
    return nil;

  NSString* localeString = [[NSLocale currentLocale] localeIdentifier];
  NSString* formattedNum = @"";
  NSRange range;
  range.length = 3;
  range.location = 3;
  // Returns the phone number 2032225200 as (203) 222-5200
  if([localeString isEqualToString:@"en_US"]) {
    NSString* areaCode = [[self.phone stringValue] substringToIndex:3];
    NSString* phone1 = [[self.phone stringValue] substringWithRange:range];
    NSString* phone2 = [[self.phone stringValue] substringFromIndex:6];
    
    formattedNum = [NSString stringWithFormat:@"(%@) %@-%@", areaCode, phone1, phone2];
  }
  
  return formattedNum;
}

- (id)valueForUndefinedKey:(NSString*)key {
  return nil;
}

@end
