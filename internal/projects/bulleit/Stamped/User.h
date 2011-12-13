//
//  User.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

extern const CGFloat kMediumUserImageSize;

typedef enum {
  StampImageSize12 = 12,
  StampImageSize14 = 14,
  StampImageSize18 = 18,
  StampImageSize28 = 28,
  StampImageSize32 = 32,
  StampImageSize42 = 42,
  StampImageSize46 = 46,
  StampImageSize60 = 60,
  StampImageSize270 = 270
} StampImageSize;

@interface User : NSManagedObject

@property (nonatomic, retain) NSString* bio;
@property (nonatomic, retain) NSString* primaryColor;
@property (nonatomic, retain) NSString* name;
@property (nonatomic, retain) NSString* imageURL;
@property (nonatomic, retain) NSString* identifier;
@property (nonatomic, retain) NSString* userID;
@property (nonatomic, retain) NSString* website;
@property (nonatomic, retain) NSString* location;
@property (nonatomic, retain) NSString* secondaryColor;
@property (nonatomic, retain) NSString* screenName;
@property (nonatomic, retain) NSSet* stamps;
@property (nonatomic, retain) NSSet* comments;
@property (nonatomic, retain) NSSet* events;
@property (nonatomic, retain) NSSet* credits;
@property (nonatomic, retain) NSSet* following;
@property (nonatomic, retain) NSSet* followers;
@property (nonatomic, retain) NSNumber* numCredits;
@property (nonatomic, retain) NSNumber* numFollowers;
@property (nonatomic, retain) NSNumber* numFriends;
@property (nonatomic, retain) NSNumber* numStamps;
@property (nonatomic, retain) NSNumber* numStampsLeft;

@property (nonatomic, readonly) NSString* profileImageURL;
@property (nonatomic, readonly) NSString* largeProfileImageURL;

- (UIImage*)invertedStampImageWithSize:(StampImageSize)size;
- (UIImage*)stampImageWithSize:(StampImageSize)size;
@end

@interface User (CoreDataGeneratedAccessors)
- (void)addFollowing:(NSSet*)values;
- (void)addFollowingObject:(NSManagedObject*)value;
- (void)removeFollowing:(NSSet*)values;
- (void)removeFollowingObject:(NSManagedObject*)value;
- (void)addStampsObject:(NSManagedObject*)value;
- (void)removeStampsObject:(NSManagedObject*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;
@end
