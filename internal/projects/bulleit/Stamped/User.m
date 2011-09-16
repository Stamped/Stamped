//
//  User.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "User.h"

#import "Util.h"

const CGFloat kMediumUserImageSize = 41.0;

@interface User ()
- (void)generateStampImage;
@end

@implementation User
@dynamic bio;
@dynamic primaryColor;
@dynamic name;
@dynamic userID;
@dynamic website;
@dynamic secondaryColor;
@dynamic profileImageURL;
@dynamic screenName;
@dynamic stampImage;
@dynamic stamps;
@dynamic events;
@dynamic comments;
@dynamic credits;
@dynamic numCredits;
@dynamic numFriends;
@dynamic numFollowers;
@dynamic numStamps;

- (void)generateStampImage {
  if (!self.primaryColor)
    return;

  self.stampImage = [Util stampImageForUser:self];
}

- (NSString*)profileImageURL {
  return [NSString stringWithFormat:@"http://static.stamped.com/users/%@-144x144.jpg", self.screenName];
}

- (void)awakeFromFetch {
  [super awakeFromFetch];
  if (!self.stampImage)
    [self generateStampImage];
}

@end
