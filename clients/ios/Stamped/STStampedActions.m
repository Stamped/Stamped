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
#import "STActionManager.h"
#import "STUserViewController.h"
#import "STPhotoViewController.h"
#import "STCreateStampViewController.h"

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
        EntityDetailViewController* detailViewController = [[[EntityDetailViewController alloc] initWithEntityID:source.sourceID] autorelease] ;
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
          [Util globalLoadingLock];
          [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
            [Util globalLoadingUnlock];
            if (stamp) {
              [[Util sharedNavigationController] pushViewController:[[[STStampDetailViewController alloc] initWithStamp:stamp] autorelease]
                                                           animated:YES];
            }
            else {
              [Util warnWithMessage:[NSString stringWithFormat:@"Stamp loading failed for stamp %@!\n%@", source.sourceID, error] andBlock:nil];
            }
          }];
        }
      }
      if (controller) {
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_view_user"] && source.sourceID != nil) {
      UIViewController* controller = nil;
      if (context.user) {
        controller = [[[STUserViewController alloc] initWithUser:source] autorelease];
      }
      else {
        controller = [[[STUserViewController alloc] initWithUser:source] autorelease];
      }
      if (controller) {
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_like_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] likeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
          if (context.completionBlock) {
            context.completionBlock(stamp, error);
          }
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_unlike_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] unlikeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
          if (context.completionBlock) {
            context.completionBlock(stamp, error);
          }
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_todo_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
          if (stamp) {
            [[STStampedAPI sharedInstance] todoWithStampID:stamp.stampID entityID:stamp.entity.entityID andCallback:^(id<STTodo> todo, NSError* error2, STCancellation* can2) {
              if (context.completionBlock) {
                context.completionBlock(todo, error2);
              }
            }];
          }
          else {
            if (context.completionBlock) {
              context.completionBlock(nil, error);
            }
          }
        }];
      }
    }
    else if ([action isEqualToString:@"stamped_untodo_stamp"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
        void (^block)(id<STStamp>, NSError*, STCancellation*) = ^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
          [[STStampedAPI sharedInstance] untodoWithStampID:stamp.stampID entityID:stamp.entity.entityID andCallback:^(BOOL success, NSError * error, STCancellation* can2) {
            if (context.completionBlock) {
              context.completionBlock([NSNumber numberWithBool:success], error);
            }
          }];
        };
        if (context.stamp) {
          block(context.stamp, nil, [STCancellation cancellation]);
        }
        else {
          [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:block];
        }
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
    else if ([action isEqualToString:@"stamped_view_image"] && source.sourceID != nil) {
      handled = YES;
      if (flag) {
          STPhotoViewController *controller = [[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:source.sourceID]];
          [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_view_create_stamp"] && source.sourceID != nil) {
        handled = YES;
        if (flag) {
            STCreateStampViewController* controller = [[[STCreateStampViewController alloc] initWithEntityID:source.sourceID] autorelease];
            [[Util sharedNavigationController] pushViewController:controller animated:YES];
        }
    }
    else if ([action isEqualToString:@"menu"] && source.sourceID != nil && context.entityDetail) {
      handled = YES;
      if (flag) {
        [Util globalLoadingLock];
        [[STStampedAPI sharedInstance] menuForEntityID:source.sourceID andCallback:^(id<STMenu> menu, NSError* error, STCancellation* cancellation) {
          [Util globalLoadingUnlock];
          NSAssert(context.entityDetail != nil, @"Context was modified after action was chosen"); 
          if (menu) {
            UIView* popUp = [[[STMenuPopUp alloc] initWithEntityDetail:context.entityDetail andMenu:menu] autorelease];
            [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.75]];
            if (context.completionBlock) {
              context.completionBlock(menu, nil);
            }
          }
          else {
            [Util warnWithMessage:[NSString stringWithFormat:@"Menu loading failed.\n%@", error] andBlock:^{
              if (context.completionBlock) {
                context.completionBlock(nil, error); 
              }
            }];
          }
        }];
      }
    }
  }
  return handled;
}

- (void)viewStampWithStampID:(NSString*)stampID {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewStamp:stampID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)viewUserWithUserID:(NSString*)userID {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewUser:userID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
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

+ (id<STAction>)actionViewImage:(NSString*)imageURL withOutputContext:(STActionContext*)context {
  return [STSimpleAction actionWithType:@"stamped_view_image" 
                              andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:imageURL]];
}

+ (id<STAction>)actionViewCreateStamp:(NSString*)entityID creditScreenNames:(NSArray*)screenNames withOutputContext:(STActionContext*)context {
    context.creditedScreenNames = [screenNames copy];
    return [STSimpleAction actionWithType:@"stamped_view_create_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:entityID]];
    
}

@end
