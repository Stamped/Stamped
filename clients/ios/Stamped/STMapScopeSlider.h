//
//  STMapScopeSlider.h
//  Stamped
//
//  Created by Andrew Bonventre on 2/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

typedef enum {
  STMapScopeSliderGranularityYou = 0,
  STMapScopeSliderGranularityFriends,
  STMapScopeSliderGranularityFriendsOfFriends,
  STMapScopeSliderGranularityEveryone
} STMapScopeSliderGranularity;

@class STMapScopeSlider;

@protocol STMapScopeSliderDelegate
- (void)mapScopeSlider:(STMapScopeSlider*)slider didChangeGranularity:(STMapScopeSliderGranularity)granularity;
@end

@interface STMapScopeSlider : UISlider

- (void)setGranularity:(STMapScopeSliderGranularity)granularity animated:(BOOL)animated;

@property (nonatomic, assign) IBOutlet id<STMapScopeSliderDelegate> delegate;
@property (nonatomic, readonly) STMapScopeSliderGranularity granularity;

@end
