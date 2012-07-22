//
//  STMapIndicatorView.h
//  Stamped
//
//  Created by Andrew Bonventre on 2/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

typedef enum {
  STMapIndicatorViewModeHidden = 0,
  STMapIndicatorViewModeLoading,
  STMapIndicatorViewModeNoResults,
  STMapIndicatorViewModeNoConnection
} STMapIndicatorViewMode;

@interface STMapIndicatorView : UIView

@property (nonatomic, assign) STMapIndicatorViewMode mode;

@end
