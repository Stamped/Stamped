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

- (id)initWithFrame:(CGRect)frame;
- (void)appendChild:(UIView*)child;

@property (nonatomic, retain) id<STViewDelegate> delegate;

@end
