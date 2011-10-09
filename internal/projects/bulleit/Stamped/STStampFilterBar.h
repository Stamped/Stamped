//
//  STStampFilterBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

typedef enum {
  StampFilterTypeNone = 0,
  StampFilterTypeFood,
  StampFilterTypeBook,
  StampFilterTypeMusic,
  StampFilterTypeFilm,
  StampFilterTypeOther
} StampFilterType;

typedef enum {
  StampSortTypeTime = 0,
  StampSortTypeDistance,
  StampSortTypePopularity
} StampSortType;

@class STStampFilterBar;
@protocol STStampFilterBarDelegate

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType 
          withSortType:(StampSortType)sortType
              andQuery:(NSString*)query;
@end

@interface STStampFilterBar : UIView

@property (nonatomic, assign) id<STStampFilterBarDelegate> delegate;

@end
