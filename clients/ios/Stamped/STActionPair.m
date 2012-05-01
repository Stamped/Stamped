//
//  STActionPair.m
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionPair.h"
#import "STActionManager.h"

@implementation STActionPair

@synthesize action = action_;
@synthesize context = context_;

- (void)executeActionWithArg:(id)notImportant {
  [self executeAction];
}

- (void)executeAction {
  id<STAction> action = self.action;
  if (action) {
    STActionContext* context = self.context;
    if (!context) {
      context = [STActionContext context];
    }
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
  }
}

+ (STActionPair*)actionPairWithAction:(id<STAction>)action {
  STActionPair* pair = [[[STActionPair alloc] init] autorelease];
  pair.action = action;
  return pair;
}

+ (STActionPair*)actionPairWithAction:(id<STAction>)action andContext:(STActionContext*)context {
  STActionPair* pair = [STActionPair actionPairWithAction:action];
  pair.context = context;
  return pair;
}

@end
