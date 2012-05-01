//
//  STActionPair.h
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STActionContext.h"

@interface STActionPair : NSObject

- (void)executeActionWithArg:(id)notImportant;
- (void)executeAction;

@property (nonatomic, readwrite, retain) id<STAction> action;
@property (nonatomic, readwrite, retain) STActionContext* context;

+ (STActionPair*)actionPairWithAction:(id<STAction>)action;
+ (STActionPair*)actionPairWithAction:(id<STAction>)action andContext:(STActionContext*)context;

@end
