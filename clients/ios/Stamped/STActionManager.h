//
//  STActionManager.h
//  Stamped
//
//  Created by Landon Judkins on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STViewDelegate.h"

@interface STActionManager : NSObject <STViewDelegate>

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action;
- (void)didChooseAction:(id<STAction>)action;
- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action;

+ (STActionManager*)sharedActionManager;

@end
