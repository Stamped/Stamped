//
//  STStampedActions.m
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedActions.h"
#import "STSimpleAction.h"
#import "STSimpleSource.h"
#import "EntityDetailViewController.h"
#import "STStampDetailViewController.h"
#import "STStampedAPI.h"
#import "STMenuPopUp.h"

@interface STStampedActions ()

- (BOOL)didChooseSource:(id<STSource>)source 
              forAction:(NSString*)action 
            withContext:(STActionContext*)context 
          shouldExecute:(BOOL)flag;
@end

@implementation STStampedActions

static STStampedActions* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STStampedActions alloc] init];
}

+ (STStampedActions*)sharedInstance {
  return _sharedInstance;
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
  return [self didChooseSource:source forAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
  [self didChooseSource:source forAction:action withContext:context shouldExecute:YES];
}


- (BOOL)didChooseSource:(id<STSource>)source 
              forAction:(NSString*)action 
            withContext:(STActionContext*)context 
          shouldExecute:(BOOL)flag {
  BOOL handled = NO;
  if ([source.source isEqualToString:@"stamped"]) {
    if ([action isEqualToString:@"stamped_view_entity"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        EntityDetailViewController* detailViewController = [[EntityDetailViewController alloc] initWithEntityID:source.sourceID] ;
        //detailViewController.referringStamp = stamp_;
        [[Util sharedNavigationController] pushViewController:detailViewController animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_view_stamp"] && source.sourceID != nil) {
      UIViewController* controller = nil;
      if (context.stamp) {
        handled = YES;
        if (flag) {
          controller = [[[STStampDetailViewController alloc] initWithStamp:context.stamp] autorelease];
        }
      }
      else {
        handled = YES;
        if (flag) {
          controller = [[[STStampDetailViewController alloc] initWithStampID:source.sourceID] autorelease];
        }
      }
      if (controller) {
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_view_user"] && source.sourceID != nil) {
      UIViewController* controller = nil;
      if (context.user) {
        //ProfileViewController* profileViewController = [[ProfileViewController alloc] init];
        //profileViewController.user = context.user;
        //controller = profileViewController;
      }
      if (controller) {
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_like_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] likeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error) {
          if (context.completionBlock) {
            context.completionBlock(stamp, error);
          }
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_unlike_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] unlikeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error) {
          if (context.completionBlock) {
            context.completionBlock(stamp, error);
          }
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_todo_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:^(id<STStamp> stamp) {
          [[STStampedAPI sharedInstance] todoWithStampID:stamp.stampID entityID:stamp.entity.entityID andCallback:^(id<STTodo> todo, NSError* error) {
            if (context.completionBlock) {
              context.completionBlock(todo, error);
            }
          }];
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_delete_stamp"] && source.sourceID != nil) {
      handled = YES;
      NSLog(@"delete");
      if (flag) {
        [[STStampedAPI sharedInstance] deleteStampWithStampID:source.sourceID andCallback:^(BOOL success, NSError* error) {
          if (context.completionBlock) {
            context.completionBlock([NSNumber numberWithBool:success], error);
          }
        }];
      }
    }
    else if ([action isEqualToString:@"menu"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [Util globalLoadingLock];
        [[STStampedAPI sharedInstance] menuForEntityID:source.sourceID andCallback:^(id<STMenu> menu) {
          [Util globalLoadingUnlock];
          if (menu && context.entityDetail) {
            UIView* popUp = [[[STMenuPopUp alloc] initWithEntityDetail:context.entityDetail andMenu:menu] autorelease];
            [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.75]];
          }
          else {
            [Util warnWithMessage:@"Menu loading failed." andBlock:nil];
          }
        }];
      }
    }
  }
  return handled;
}

+ (id<STAction>)actionViewEntity:(NSString*)entityID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_view_entity" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:entityID]];
}

+ (id<STAction>)actionViewStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_view_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionViewUser:(NSString*)userID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_view_user" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:userID]];
}

+ (id<STAction>)actionLikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_like_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionUnlikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_unlike_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionTodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_todo_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionUntodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_untodo_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionDeleteStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_delete_stamp" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

@end
