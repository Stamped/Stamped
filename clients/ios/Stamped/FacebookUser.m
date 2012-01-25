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

- (BOOL)isEqual:(id)object {
  if (object == self)
    return YES;
  if (!object || ![object isKindOfClass:[FacebookUser class]])
    return NO;
  
  return [self.facebookID isEqualToString:[(FacebookUser*)object facebookID]];
}

- (NSUInteger)hash {
  return facebookID_.hash;
}

@end
