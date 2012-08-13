//
//  STScrollViewContainer.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STViewDelegate.h"

@interface STScrollViewContainer : UIScrollView <STViewDelegate, STViewDelegateDependent>

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame;
- (void)appendChildView:(UIView*)child;
- (void)removeChildView:(UIView*)view withAnimation:(BOOL)animation __attribute__ ((deprecated));
- (void)reloadStampedData;
- (void)updateContentSize __attribute__ ((deprecated));

@property (nonatomic, readwrite, assign) id<UIScrollViewDelegate> scrollDelegate;

@end
