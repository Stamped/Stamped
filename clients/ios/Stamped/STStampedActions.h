//
//  STStampedActions.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActionDelegate.h"

@interface STStampedActions : NSObject <STActionDelegate>

+ (STStampedActions*)sharedInstance;

+ (id<STAction>)actionViewEntity:(NSString*)entityID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionViewStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionViewUser:(NSString*)userID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionLikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionUnlikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionTodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionUntodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;
+ (id<STAction>)actionDeleteStamp:(NSString*)stampID withOutputContext:(STActionContext*)context;

@end
