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

- (void)setCoordinates:(NSString*)coordinates {
  [self willChangeValueForKey:@"coordinates"];
  [self setPrimitiveValue:coordinates forKey:@"coordinates"];
  NSArray* coordinatesArray = [self.coordinates componentsSeparatedByString:@","]; 
  CGFloat latitude = [(NSString*)[coordinatesArray objectAtIndex:0] floatValue];
  CGFloat longitude = [(NSString*)[coordinatesArray objectAtIndex:1] floatValue];
  self.location = [[[CLLocation alloc] initWithLatitude:latitude longitude:longitude] autorelease];  
  [self didChangeValueForKey:@"coordinates"];
}

- (id)valueForUndefinedKey:(NSString*)key {
  return nil;
}

// TODO(andybons): Remove for launch.
- (void)awakeFromFetch {
  [super awakeFromFetch];
  if (self.coordinates && !self.location)
    [self setCoordinates:self.coordinates];
}

@end
