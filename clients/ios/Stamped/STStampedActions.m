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
  
}


- (BOOL)didChooseSource:(id<STSource>)source 
              forAction:(NSString*)action 
            withContext:(STActionContext*)context 
          shouldExecute:(BOOL)flag {
  BOOL handled = NO;
  if ([source.source isEqualToString:@"stamped"]) {
    if ([action isEqualToString:@"stamped_view_entity"] && source.sourceID != nil) {
      EntityDetailViewController* detailViewController = [[EntityDetailViewController alloc] initWithEntityID:source.sourceID] ;
      //detailViewController.referringStamp = stamp_;
      [[Util sharedNavigationController] pushViewController:detailViewController animated:YES];
    }
    else if ([action isEqualToString:@"stamped_view_stamp"] && source.sourceID != nil) {
      UIViewController* controller = nil;
      if (context.stamp) {
        controller = [[[STStampDetailViewController alloc] initWithStamp:context.stamp] autorelease];
      }
      if (controller) {
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }
    }
    else if ([action isEqualToString:@"stamped_view_user"] && source.sourceID != nil) {
      
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

@end
