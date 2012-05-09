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

@interface STTodoButton ()

@property (nonatomic, readwrite, assign) BOOL waiting;

@end

@implementation STTodoButton

@synthesize waiting = waiting_;

- (id)initWithStamp:(id<STStamp>)stamp
{
  self = [super initWithStamp:stamp normalOffImage:[UIImage imageNamed:@"sDetailBar_btn_todo"] offText:@"To-Do" andOnText:@"To-Do'd"];
  if (self) {
    self.normalOnImage = [UIImage imageNamed:@"sDetailBar_btn_todo_selected"];
    self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_todo_active"];
    self.touchedOnImage = [UIImage imageNamed:@"sDetailBar_btn_todo_active"];
    self.on = [[self.stamp isTodod] boolValue];
  }
  return self;
}

- (void)defaultHandler:(id)myself {
  if (self.stamp && !self.waiting) {
    self.waiting = YES;
    STActionContext* context = [STActionContext contextWithCompletionBlock:^(id stamp, NSError* error) {
      self.waiting = NO;
      if (!error) {
        [Util reloadStampedData];
      }
      else {
        self.on = !self.on;
        [Util warnWithMessage:@"Todo failed; see log" andBlock:nil];
      }
    }];
    context.stamp = self.stamp;
    id<STAction> action;
    if (self.stamp.isTodod.boolValue) {
      action = [STStampedActions actionUntodoStamp:self.stamp.stampID withOutputContext:context];
    }
    else {
      action = [STStampedActions actionTodoStamp:self.stamp.stampID withOutputContext:context];
    }
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    self.on = !self.on;
  }
}

- (void)setStamp:(id<STStamp>)stamp {
  [super setStamp:stamp];
  self.on = stamp.isTodod.boolValue;
}

@end
