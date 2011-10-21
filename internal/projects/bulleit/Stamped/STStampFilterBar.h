//
//  STStampFilterBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

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

@class STStampFilterBar;

@protocol STStampFilterBarDelegate
- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query;
@end

@interface STStampFilterBar : UIView <UIScrollViewDelegate, UITextFieldDelegate>

@property (nonatomic, assign) IBOutlet id<STStampFilterBarDelegate> delegate;
@property (nonatomic, assign) StampFilterType filterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, readonly) STSearchField* searchField;

- (void)reset;

@end
