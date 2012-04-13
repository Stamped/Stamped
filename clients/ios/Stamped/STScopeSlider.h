//
//  STInboxScopeSlider.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStampedAPI.h"

@class STScopeSlider;

@protocol STScopeSliderDelegate
- (void)scopeSlider:(STScopeSlider*)slider didChangeGranularity:(STStampedAPIScope)granularity;
@end

@interface STScopeSlider : UISlider

- (void)flashTooltip;
- (void)setGranularity:(STStampedAPIScope)granularity animated:(BOOL)animated;

@property (nonatomic, assign) id<STScopeSliderDelegate> delegate;
@property (nonatomic, readonly) STStampedAPIScope granularity;

@end
