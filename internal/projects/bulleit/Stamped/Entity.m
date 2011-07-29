//
//  Entity.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Entity.h"
#import "Stamp.h"


@implementation Entity

@dynamic category;
@dynamic categoryImage;
@dynamic entityID;
@dynamic subtitle;
@dynamic title;
@dynamic coordinates;
@dynamic stamps;

- (void)awakeFromFetch {
  [super awakeFromFetch];
  if (!self.categoryImage) {
    self.categoryImage =
    [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[self.category lowercaseString]]];
  }
}

@end
