//
//  Entity.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Stamp;

typedef enum {
  EntityCategoryOther,
  EntityCategoryBook,
  EntityCategoryFilm,
  EntityCategoryMusic,
  EntityCategoryPlace
} EntityCategory;

@interface Entity : NSManagedObject

@property (nonatomic, retain) NSString* category;
@property (nonatomic, retain) UIImage* categoryImage;
@property (nonatomic, retain) NSString* entityID;
@property (nonatomic, retain) NSString* subtitle;
@property (nonatomic, retain) NSString* title;
@property (nonatomic, retain) NSString* coordinates;
@property (nonatomic, retain) NSSet* stamps;

@property (nonatomic, readonly) EntityCategory entityCategory;
@end

@interface Entity (CoreDataGeneratedAccessors)

- (void)addStampsObject:(Stamp*)value;
- (void)removeStampsObject:(Stamp*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;

@end
