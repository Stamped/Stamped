//
//  STViewContainer.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STViewDelegate.h"

@interface STViewContainer : UIView <STViewDelegate, STViewDelegateDependent>

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame;
- (void)appendChildView:(UIView*)child;
- (void)appendChildView:(UIView*)child withAnimation:(BOOL)animation __attribute__ ((deprecated));
- (void)removeChildView:(UIView*)child withAnimation:(BOOL)animation __attribute__ ((deprecated));
- (void)reloadStampedData;

@end
