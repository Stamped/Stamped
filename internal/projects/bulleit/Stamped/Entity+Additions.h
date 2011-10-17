//
//  Entity.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

#import "Entity.h"

@class CLLocation;

typedef enum {
  EntityCategoryOther,
  EntityCategoryBook,
  EntityCategoryFilm,
  EntityCategoryMusic,
  EntityCategoryFood
} EntityCategory;

@interface Entity (Additions)

@property (nonatomic, readonly) EntityCategory entityCategory;
@property (nonatomic, readonly) UIImage* categoryImage;
@property (nonatomic, retain) NSNumber* cachedDistance;

@end