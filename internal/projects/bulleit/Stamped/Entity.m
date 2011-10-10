//
//  Entity.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <CoreLocation/CoreLocation.h>

#import "Entity.h"
#import "Event.h"
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
@dynamic events;
@dynamic location;

@synthesize cachedDistance = cachedDistance_;

- (void)dealloc {
  self.cachedDistance = nil;
  [super dealloc];
}

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

- (CLLocation*)location {
  if (!self.coordinates)
    return nil;
  
  NSArray* coordinates = [self.coordinates componentsSeparatedByString:@","]; 
  CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
  return [[[CLLocation alloc] initWithLatitude:latitude longitude:longitude] autorelease];
}

- (id)valueForUndefinedKey:(NSString*)key {
  return nil;
}

@end
