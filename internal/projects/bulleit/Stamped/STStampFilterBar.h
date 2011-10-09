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
  StampFilterTypeOther,
  StampFilterTypeTime,
  StampFilterTypeDistance,
  StampFilterTypePopularity
} StampFilterType;

@class STStampFilterBar;
@protocol STStampFilterBarDelegate

- (void)filterBar:(STStampFilterBar*)bar didSelectFilter:(StampFilterType)filterType;
- (void)filterBar:(STStampFilterBar*)bar didFilterByQuery:(NSString*)query;
@end

@interface STStampFilterBar : UIView

@property (nonatomic, assign) id<STStampFilterBarDelegate> delegate;

@end
