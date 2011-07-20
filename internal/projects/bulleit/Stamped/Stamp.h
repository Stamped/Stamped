//
//  Stamp.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class User;
@class Entity;

typedef enum {
  StampCategoryOther,
  StampCategoryBook,
  StampCategoryFilm,
  StampCategoryMusic,
  StampCategoryPlace
} StampCategory;

@interface Stamp : NSManagedObject

@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) User* user;
@property (nonatomic, retain) Entity* entityObject;

@property (nonatomic, readonly) StampCategory category;
@property (nonatomic, readonly) UIImage* categoryImage;
@property (nonatomic, retain) UIImage* stampImage;

@end
