//
//  Stamp.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>
#import "STStamp.h"

@class Comment, Entity, Event, Favorite, User;

@interface Stamp : NSManagedObject

@property (nonatomic, readwrite, retain) NSString* blurb;
@property (nonatomic, readwrite, retain) NSDate* created;
@property (nonatomic, readwrite, retain) NSNumber* deleted;
@property (nonatomic, readwrite, retain) NSString* imageDimensions;
@property (nonatomic, readwrite, retain) NSString* imageURL;
@property (nonatomic, readwrite, retain) NSNumber* isFavorited;
@property (nonatomic, readwrite, retain) NSNumber* isLiked;
@property (nonatomic, readwrite, retain) NSDate* modified;
@property (nonatomic, readwrite, retain) NSNumber* numComments;
@property (nonatomic, readwrite, retain) NSNumber* numLikes;
@property (nonatomic, readwrite, retain) NSString* stampID;
@property (nonatomic, readwrite, retain) NSString* URL;
@property (nonatomic, readwrite, retain) NSString* via;
@property (nonatomic, readwrite, retain) NSSet* comments;
@property (nonatomic, readwrite, retain) NSSet* credits;
@property (nonatomic, readwrite, retain) Entity* entityObject;
@property (nonatomic, readwrite, retain) NSSet* events;
@property (nonatomic, readwrite, retain) NSSet* favorites;
@property (nonatomic, readwrite, retain) User* user;

@end

@interface Stamp (CoreDataGeneratedAccessors)

- (void)addCommentsObject:(Comment *)value;
- (void)removeCommentsObject:(Comment *)value;
- (void)addComments:(NSSet *)values;
- (void)removeComments:(NSSet *)values;
- (void)addCreditsObject:(User *)value;
- (void)removeCreditsObject:(User *)value;
- (void)addCredits:(NSSet *)values;
- (void)removeCredits:(NSSet *)values;
- (void)addEventsObject:(Event *)value;
- (void)removeEventsObject:(Event *)value;
- (void)addEvents:(NSSet *)values;
- (void)removeEvents:(NSSet *)values;
- (void)addFavoritesObject:(Favorite *)value;
- (void)removeFavoritesObject:(Favorite *)value;
- (void)addFavorites:(NSSet *)values;
- (void)removeFavorites:(NSSet *)values;
@end
