//
//  STViewContainer.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STViewDelegate.h"

@interface STViewContainer : UIView <STViewDelegate>

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame;
- (void)appendChildView:(UIView*)child;

@property (nonatomic, assign) id<STViewDelegate> delegate;

@end
