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

typedef enum {
  STStampFilterBarStyleDefault,
  STStampFilterBarStyleDark
} STStampFilterBarStyle;

@class STStampFilterBar;

@protocol STStampFilterBarDelegate
@required
- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query;
- (void)stampFilterBarSearchFieldDidBeginEditing;
- (void)stampFilterBarSearchFieldDidEndEditing;
@end

@interface STStampFilterBar : UIView <UIScrollViewDelegate, UITextFieldDelegate>

- (id)initWithFrame:(CGRect)frame style:(STStampFilterBarStyle)style;

@property (nonatomic, assign) IBOutlet id<STStampFilterBarDelegate> delegate;
@property (nonatomic, assign) StampFilterType filterType;
@property (nonatomic, copy) NSString* searchQuery;
@property (nonatomic, readonly) STSearchField* searchField;
@property (nonatomic, readonly) UIImageView* tooltipImageView;

- (void)reset;

@end
