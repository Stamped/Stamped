//
//  STViewDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STViewDelegateDependent.h"

@protocol STViewDelegate <NSObject>
@optional
- (void)didChooseAction:(id<STAction>)action;
- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action;
- (void)childView:(UIView*)view shouldChangeHeightBy:(CGFloat)delta overDuration:(CGFloat)seconds;
- (void)registerDependent:(id<STViewDelegateDependent>)dependent;

@end

typedef UIView* (^STViewCreator)(id<STViewDelegate>);
typedef void (^STViewCreatorCallback)(STViewCreator);