//
//  STInboxScopeSlider.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

typedef enum {
  STScopeSliderGranularityYou = 0,
  STScopeSliderGranularityFriends,
  STScopeSliderGranularityFriendsOfFriends,
  STScopeSliderGranularityEveryone
} STScopeSliderGranularity;

@class STInboxScopeSlider;

@protocol STScopeSliderDelegate
- (void)scopeSlider:(STInboxScopeSlider*)slider didChangeGranularity:(STScopeSliderGranularity)granularity;
@end

@interface STInboxScopeSlider : UISlider

- (void)flashTooltip;
- (void)setGranularity:(STScopeSliderGranularity)granularity animated:(BOOL)animated;

@property (nonatomic, assign) id<STScopeSliderDelegate> delegate;
@property (nonatomic, readonly) STScopeSliderGranularity granularity;

@end
