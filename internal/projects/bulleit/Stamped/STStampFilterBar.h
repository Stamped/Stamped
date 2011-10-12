//
//  STStampFilterBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <CoreLocation/CoreLocation.h>
#import <UIKit/UIKit.h>

@class STSearchField;

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

@interface STStampFilterBar : UIView <UIScrollViewDelegate, UITextFieldDelegate, CLLocationManagerDelegate>

@property (nonatomic, assign) IBOutlet id<STStampFilterBarDelegate> delegate;
@property (nonatomic, assign) StampFilterType filterType;
@property (nonatomic, assign) StampSortType sortType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, retain) CLLocation* currentLocation;
@property (nonatomic, readonly) CLLocationManager* locationManager;
@property (nonatomic, readonly) STSearchField* searchField;

- (void)reset;

@end
