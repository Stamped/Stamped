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
