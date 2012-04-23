//
//  STTodoButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTodoButton.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "Util.h"
#import "STStampedAPI.h"

@implementation STTodoButton

- (id)initWithStamp:(id<STStamp>)stamp
{
  self = [super initWithStamp:stamp normalOffImage:[UIImage imageNamed:@"toolbar_todoButton"] offText:@"To-Do" andOnText:@"To-Do'd"];
  if (self) {
    self.normalOnImage = [UIImage imageNamed:@"toolbar_todoButton_selected"];
    self.touchedOffImage = [UIImage imageNamed:@"toolbar_todoButton_highlighted"];
    self.touchedOnImage = [UIImage imageNamed:@"toolbar_todoButton_highlighted"];
    self.on = [[self.stamp isTodod] boolValue];
  }
  return self;
}

- (void)defaultHandler:(id)myself {
  if (self.stamp) {
    STActionContext* context = [STActionContext contextWithCompletionBlock:^(id stamp, NSError* error) {
      if (!error) {
        [Util reloadStampedData];
      }
      else {
        [Util warnWithMessage:@"Todo failed; see log" andBlock:nil];
      }
    }];
    id<STAction> action;
    if (self.stamp.isTodod.boolValue) {
      action = [STStampedActions actionUntodoStamp:self.stamp.stampID withOutputContext:context];
    }
    else {
      action = [STStampedActions actionTodoStamp:self.stamp.stampID withOutputContext:context];
    }
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
  }
}

- (void)setStamp:(id<STStamp>)stamp {
  [super setStamp:stamp];
  self.on = stamp.isTodod.boolValue;
}

@end
