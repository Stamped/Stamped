//
//  SearchResult.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchResult.h"

@implementation SearchResult

@synthesize title = title_;
@synthesize category = category_;
@synthesize subtitle = subtitle_;
@synthesize searchID = searchID_;
@synthesize entityID = entityID_;
@synthesize distance = distance_;

- (void)dealloc {
  self.distance = nil;
  [super dealloc];
}

- (SearchCategory)searchCategory {
  NSString* cat = self.category;
  if ([cat isEqualToString:@"food"]) {
    return SearchCategoryFood;
  } else if ([cat isEqualToString:@"film"]) {
    return SearchCategoryFilm;
  } else if ([cat isEqualToString:@"music"]) {
    return SearchCategoryMusic;
  } else if ([cat isEqualToString:@"book"]) {
    return SearchCategoryBook;
  }
  return SearchCategoryOther;
}

- (UIImage*)categoryImage {
  if (self.category)
    return [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[self.category lowercaseString]]];
  
  return [UIImage imageNamed:@"cat_icon_other"];
}

- (UIImage*)largeCategoryImage {
  if (self.category)
    return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_%@_large", [self.category lowercaseString]]];
  
  return [UIImage imageNamed:@"cat_icon_other_large"];
}

@end
