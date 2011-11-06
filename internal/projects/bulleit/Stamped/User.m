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
- (void)refreshStampImage;
@end

@implementation User
@dynamic bio;
@dynamic primaryColor;
@dynamic name;
@dynamic userID;
@dynamic website;
@dynamic secondaryColor;
@dynamic profileImageURL;
@dynamic largeProfileImageURL;
@dynamic location;
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
@dynamic numStampsLeft;
@dynamic imageURL;
@dynamic identifier;

- (void)setPrimaryColor:(NSString*)primaryColor {
  [self willChangeValueForKey:@"primaryColor"];
  BOOL refreshImage = ![self.primaryColor isEqualToString:primaryColor];
  [self setPrimitiveValue:primaryColor forKey:@"primaryColor"];
  if (refreshImage)
    [self refreshStampImage];

  [self didChangeValueForKey:@"primaryColor"];
}

- (void)setSecondaryColor:(NSString*)secondaryColor {
  [self willChangeValueForKey:@"secondaryColor"];
  BOOL refreshImage = ![self.secondaryColor isEqualToString:secondaryColor];
  [self setPrimitiveValue:secondaryColor forKey:@"secondaryColor"];
  if (refreshImage)
    [self refreshStampImage];

  [self didChangeValueForKey:@"secondaryColor"];
}

- (void)refreshStampImage {
  if (!self.primaryColor)
    return;

  self.stampImage = [Util stampImageForUser:self];
}

- (NSString*)largeProfileImageURL {
  if (self.imageURL)
    return self.imageURL;

  return [NSString stringWithFormat:@"http://static.stamped.com/users/%@.jpg", self.screenName.lowercaseString];
}

- (NSString*)profileImageURL {
  if (self.imageURL) {
    NSString* original = [NSString stringWithFormat:@"/users/%@.jpg", self.screenName.lowercaseString];
    NSString* replacement = [NSString stringWithFormat:@"/users/%@-144x144.jpg", self.screenName.lowercaseString];
    NSString* URL = [self.imageURL stringByReplacingOccurrencesOfString:original withString:replacement];
    return URL;
  }
  
  return [NSString stringWithFormat:@"http://static.stamped.com/users/%@-144x144.jpg",
      self.screenName.lowercaseString];
}


@end
