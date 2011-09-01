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

@interface User : NSManagedObject

@property (nonatomic, retain) NSString* bio;
@property (nonatomic, retain) NSString* displayName;
@property (nonatomic, retain) NSString* primaryColor;
@property (nonatomic, retain) NSString* firstName;
@property (nonatomic, retain) NSString* lastName;
@property (nonatomic, retain) NSString* userID;
@property (nonatomic, retain) NSString* website;
@property (nonatomic, retain) NSString* secondaryColor;
@property (nonatomic, retain) NSString* profileImageURL;
@property (nonatomic, retain) NSString* screenName;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, retain) NSSet* stamps;
@property (nonatomic, retain) NSSet* comments;
@property (nonatomic, retain) NSSet* events;
@property (nonatomic, retain) NSSet* credits;
@property (nonatomic, retain) NSSet* friends;
@property (nonatomic, retain) NSSet* followers;
@property (nonatomic, retain) NSNumber* numCredits;
@property (nonatomic, retain) NSNumber* numFollowers;
@property (nonatomic, retain) NSNumber* numFriends;
@property (nonatomic, retain) NSNumber* numStamps;
@end

@interface User (CoreDataGeneratedAccessors)
- (void)addFriendsObject:(NSManagedObject*)value;
- (void)removeFriendsObject:(NSManagedObject*)value;
- (void)addFriends:(NSSet*)values;
- (void)removeFriends:(NSSet*)values;

- (void)addFollowersObject:(NSManagedObject*)value;
- (void)removeFollowersObject:(NSManagedObject*)value;
- (void)addFollowers:(NSSet*)values;
- (void)removeFollowers:(NSSet*)values;

- (void)addStampsObject:(NSManagedObject*)value;
- (void)removeStampsObject:(NSManagedObject*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;
@end
