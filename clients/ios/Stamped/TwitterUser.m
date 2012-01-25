//
//  TwitterUser.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "TwitterUser.h"

@implementation TwitterUser

@synthesize name = name_;
@synthesize screenName = screenName_;
@synthesize profileImageURL = profileImageURL_;

- (BOOL)isEqual:(id)object {
  if (object == self)
    return YES;
  if (!object || ![object isKindOfClass:[TwitterUser class]])
    return NO;
  
  return [self.screenName isEqualToString:[(TwitterUser*)object screenName]];
}

- (NSUInteger)hash {
  return screenName_.hash;
}

@end
