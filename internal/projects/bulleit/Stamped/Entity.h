//
//  Entity.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Favorite;
@class Stamp;

typedef enum {
  EntityCategoryOther,
  EntityCategoryBooks,
  EntityCategoryFilm,
  EntityCategoryMusic,
  EntityCategoryFood
} EntityCategory;

@interface Entity : NSManagedObject

- (NSString*)localizedPhoneNumber;

@property (nonatomic, retain) NSString* address;
@property (nonatomic, retain) NSString* street;
@property (nonatomic, retain) NSString* substreet;
@property (nonatomic, retain) NSString* city;
@property (nonatomic, retain) NSString* state;
@property (nonatomic, retain) NSString* zipcode;
@property (nonatomic, retain) NSString* category;
@property (nonatomic, retain) NSString* entityID;
@property (nonatomic, retain) NSString* openTableURL;
@property (nonatomic, retain) NSString* subtitle;
@property (nonatomic, retain) NSString* title;
@property (nonatomic, retain) NSString* coordinates;
@property (nonatomic, retain) NSString* subcategory;
@property (nonatomic, retain) NSString* desc;
@property (nonatomic, retain) NSString* artist;
@property (nonatomic, retain) NSString* album;
@property (nonatomic, retain) NSString* authors;
@property (nonatomic, retain) NSString* cast;
@property (nonatomic, retain) NSString* director;
@property (nonatomic, retain) NSString* year;
@property (nonatomic, retain) NSSet* stamps;
@property (nonatomic, retain) NSNumber* phone;
@property (nonatomic, retain) Favorite* favorite;

@property (nonatomic, readonly) EntityCategory entityCategory;
@property (nonatomic, readonly) UIImage* categoryImage;
@property (nonatomic, readonly) UIImage* largeCategoryImage;
@end

@interface Entity (CoreDataGeneratedAccessors)

- (void)addStampsObject:(Stamp*)value;
- (void)removeStampsObject:(Stamp*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;

@end
