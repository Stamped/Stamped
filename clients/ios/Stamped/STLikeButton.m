//
//  STLikeButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLikeButton.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "Util.h"
#import "STStampedAPI.h"

@implementation STLikeButton

- (id)initWithStamp:(id<STStamp>)stamp
{
  self = [super initWithStamp:stamp normalOffImage:[UIImage imageNamed:@"sDetailBar_btn_like"] offText:@"Like" andOnText:@"Liked"];
  if (self) {
    self.normalOnImage = [UIImage imageNamed:@"sDetailBar_btn_like_selected"];
    self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_like_active"];
    self.touchedOnImage = [UIImage imageNamed:@"sDetailBar_btn_like_active"];
    self.on = [[self.stamp isLiked] boolValue];
  }
  return self;
}

- (void)defaultHandler:(id)myself {
  if (self.stamp) {
    STActionContext* context = [STActionContext contextWithCompletionBlock:^(id stamp, NSError* error) {
      if (!error) {
        [Util reloadStampedData];
      }
    }];
    id<STAction> action;
    if (self.stamp.isLiked.boolValue) {
      action = [STStampedActions actionUnlikeStamp:self.stamp.stampID withOutputContext:context];
    }
    else {
      action = [STStampedActions actionLikeStamp:self.stamp.stampID withOutputContext:context];
    }
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
  }
}

- (void)setStamp:(id<STStamp>)stamp {
  [super setStamp:stamp];
  self.on = [[self.stamp isLiked] boolValue];
}

@end
