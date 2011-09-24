//
//  SearchResult.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

typedef enum {
  SearchCategoryOther,
  SearchCategoryBook,
  SearchCategoryFilm,
  SearchCategoryMusic,
  SearchCategoryFood
} SearchCategory;

@interface SearchResult : NSObject

@property (nonatomic, copy) NSString* title;
@property (nonatomic, copy) NSString* category;
@property (nonatomic, copy) NSString* subtitle;
@property (nonatomic, copy) NSString* searchID;
@property (nonatomic, copy) NSString* entityID;

@property (nonatomic, readonly) SearchCategory searchCategory;
@property (nonatomic, readonly) UIImage* categoryImage;
@property (nonatomic, readonly) UIImage* largeCategoryImage;

@end
