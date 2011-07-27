//
//  Stamp.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/26/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

extern NSString* kStampDidChangeNotification;

@class Comment, Entity, User;

typedef enum {
  StampCategoryOther,
  StampCategoryBook,
  StampCategoryFilm,
  StampCategoryMusic,
  StampCategoryPlace
} StampCategory;

@interface Stamp : NSManagedObject

@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSNumber* numComments;
@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) User* user;
@property (nonatomic, retain) NSSet* comments;

@property (nonatomic, readonly) StampCategory category;
@end

@interface Stamp (CoreDataGeneratedAccessors)

- (void)addCommentsObject:(Comment*)value;
- (void)removeCommentsObject:(Comment*)value;
- (void)addComments:(NSSet*)values;
- (void)removeComments:(NSSet*)values;

@end
