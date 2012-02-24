//
//  Stamp.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Comment, Entity, Event, Favorite, User;

@interface Stamp : NSManagedObject

@property (nonatomic, retain) NSString * blurb;
@property (nonatomic, retain) NSDate * created;
@property (nonatomic, retain) NSNumber * deleted;
@property (nonatomic, retain) NSString * imageDimensions;
@property (nonatomic, retain) NSString * imageURL;
@property (nonatomic, retain) NSNumber * isFavorited;
@property (nonatomic, retain) NSNumber * isLiked;
@property (nonatomic, retain) NSDate * modified;
@property (nonatomic, retain) NSNumber * numComments;
@property (nonatomic, retain) NSNumber * numLikes;
@property (nonatomic, retain) NSString * stampID;
@property (nonatomic, retain) NSNumber * temporary;
@property (nonatomic, retain) NSString * URL;
@property (nonatomic, retain) NSString * via;
@property (nonatomic, retain) NSSet *comments;
@property (nonatomic, retain) NSSet *credits;
@property (nonatomic, retain) Entity *entityObject;
@property (nonatomic, retain) NSSet *events;
@property (nonatomic, retain) NSSet *favorites;
@property (nonatomic, retain) User *user;
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
