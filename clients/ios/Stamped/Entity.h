//
//  Entity.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class CLLocation;
@class Event;
@class Favorite;
@class Stamp;

typedef enum {
  EntityCategoryOther,
  EntityCategoryBook,
  EntityCategoryFilm,
  EntityCategoryMusic,
  EntityCategoryFood
} EntityCategory;

@interface Entity : NSManagedObject

@property (nonatomic, retain) NSString* category;
@property (nonatomic, retain) NSString* coordinates;
@property (nonatomic, retain) NSString* entityID;
@property (nonatomic, retain) NSDate* localModificationDate;
@property (nonatomic, retain) NSDate* mostRecentStampDate;
@property (nonatomic, retain) NSString* subcategory;
@property (nonatomic, retain) NSString* subtitle;
@property (nonatomic, retain) NSString* title;

@property (nonatomic, retain) NSSet* events;
@property (nonatomic, retain) Favorite* favorite;
@property (nonatomic, retain) NSSet* stamps;

@property (nonatomic, readonly) EntityCategory entityCategory;
@property (nonatomic, readonly) UIImage* inboxTodoCategoryImage;
@property (nonatomic, readonly) UIImage* highlightedInboxTodoCategoryImage;
@property (nonatomic, readonly) UIImage* stampDetailCategoryImage;
@property (nonatomic, readonly) UIImage* entitySearchCategoryImage;

- (void)updateLatestStamp;
@end

@interface Entity (CoreDataGeneratedAccessors)

- (void)addEventsObject:(Event*)value;
- (void)removeEventsObject:(Event*)value;
- (void)addEvents:(NSSet*)values;
- (void)removeEvents:(NSSet*)values;
- (void)addStampsObject:(Stamp*)value;
- (void)removeStampsObject:(Stamp*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;
@end
