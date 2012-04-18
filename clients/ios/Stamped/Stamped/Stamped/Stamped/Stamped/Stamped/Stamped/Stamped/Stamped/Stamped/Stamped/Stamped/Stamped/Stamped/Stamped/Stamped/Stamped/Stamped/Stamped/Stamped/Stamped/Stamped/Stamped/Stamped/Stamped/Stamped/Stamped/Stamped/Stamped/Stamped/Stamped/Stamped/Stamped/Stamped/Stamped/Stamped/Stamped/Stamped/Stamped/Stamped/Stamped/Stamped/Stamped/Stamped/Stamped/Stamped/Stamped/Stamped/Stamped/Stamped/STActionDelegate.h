//
//  STActionDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STActionContext.h"

@protocol STActionDelegate <NSObject>
@optional
- (BOOL)canHandleAction:(id<STAction>)action withContext:(STActionContext*)context;
- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;
- (void)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context;
- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context;

@end
