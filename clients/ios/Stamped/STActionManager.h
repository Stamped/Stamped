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

extern NSString* STActionManagerShowAllActionsKey;

@interface STActionManager : NSObject <STViewDelegate>

+ (STActionManager*)sharedActionManager;

- (BOOL)lock;

- (BOOL)unlock;

+ (BOOL)lock;

+ (BOOL)unlock;

- (void)setStampContext:(id<STStamp>)stamp;

@property (nonatomic, readwrite, assign) id actionsLocked;

+ (void)setupConfigurations;

@end
