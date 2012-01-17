//
//  FacebookUser.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "FacebookUser.h"

@implementation FacebookUser

@synthesize name = name_;
@synthesize facebookID = facebookID_;
@synthesize profileImageURL = profileImageURL_;

- (NSUInteger)hash {
  return facebookID_.hash;
}

@end
