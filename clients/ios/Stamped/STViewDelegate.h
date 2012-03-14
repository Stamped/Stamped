//
//  STViewDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STFactoryDelegate.h"
#import "STResizeDelegate.h"
#import "STAction.h"

@protocol STViewDelegate <STFactoryDelegate, STResizeDelegate>

- (void)view:(UIView*)view didChooseAction:(id<STAction>)action;

@end

