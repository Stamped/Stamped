//
//  User.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "User.h"

#import "Util.h"

@implementation User
@dynamic bio;
@dynamic primaryColor;
@dynamic name;
@dynamic userID;
@dynamic website;
@dynamic secondaryColor;
@dynamic largeProfileImageURL;
@dynamic location;
@dynamic screenName;
@dynamic stamps;
@dynamic events;
@dynamic comments;
@dynamic credits;
@dynamic followers;
@dynamic following;
@dynamic numCredits;
@dynamic numFriends;
@dynamic numFollowers;
@dynamic numStamps;
@dynamic numStampsLeft;
@dynamic imageURL;
@dynamic identifier;

- (UIImage*)stampImageWithSize:(StampImageSize)size {
  return [Util gradientImage:[UIImage imageNamed:[NSString stringWithFormat:@"stamp_%dpt_texture", size]]
            withPrimaryColor:self.primaryColor
                   secondary:self.secondaryColor];
}

- (UIImage*)invertedStampImageWithSize:(StampImageSize)size {
  return [Util whiteMaskedImageUsingImage:[UIImage imageNamed:[NSString stringWithFormat:@"stamp_%dpt_texture", size]]];
}

- (NSString*)profileImageURLForSize:(ProfileImageSize)size {
  CGFloat imageSize = size * [UIScreen mainScreen].scale;
  if (self.imageURL) {
    NSString* original = [NSString stringWithFormat:@"/users/%@.jpg", self.screenName.lowercaseString];
    NSString* replacement =
        [NSString stringWithFormat:@"/users/%@-%.0fx%.0f.jpg",
            self.screenName.lowercaseString, imageSize, imageSize];
    NSString* URL = [self.imageURL stringByReplacingOccurrencesOfString:original withString:replacement];
    return URL;
  }

  return [NSString stringWithFormat:@"http://static.stamped.com/users/%@-144x144.jpg",
          self.screenName.lowercaseString];
}

- (NSString*)largeProfileImageURL {
  if (self.imageURL)
    return self.imageURL;

  return [NSString stringWithFormat:@"http://static.stamped.com/users/%@.jpg", self.screenName.lowercaseString];
}

@end
