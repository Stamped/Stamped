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

@interface STMapScopeSlider : UISlider

@end
