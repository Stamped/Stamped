//
//  STActionManager.m
//  Stamped
//
//  Created by Landon Judkins on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionManager.h"
#import "STActionMenuFactory.h"
#import "STViewDelegate.h"
#import "Util.h"
#import "STRdio.h"
#import "STMenuFactory.h"
#import "STMenuPopUp.h"
#import "STStampedActions.h"
#import "STSimpleAction.h"
#import "STStampedAPI.h"

@interface STActionManager () <STViewDelegate>

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;
- (BOOL)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;

@property (nonatomic, readonly, retain) NSOperationQueue* operationQueue;
@property (nonatomic, readonly, retain) NSMutableDictionary* sources;

@end

@implementation STActionManager

@synthesize operationQueue = _operationQueue;
@synthesize sources = _sources;
@synthesize actionsLocked = _actionsLocked;

static STActionManager* _singleton;

+ (void)initialize {
  _singleton = [[STActionManager alloc] init];
}

+ (STActionManager*)sharedActionManager {
  return _singleton;
}

- (id)init
{
  self = [super init];
  if (self) {
    _operationQueue = [[NSOperationQueue alloc] init];
    _sources = [[NSMutableDictionary alloc] init];
    [_sources setObject:[STRdio sharedRdio] forKey:@"rdio"];
    [_sources setObject:[STStampedActions sharedInstance] forKey:@"stamped"];
  }
  return self;
}

- (void)dealloc
{
  [_operationQueue release];
  [_sources release];
  [super dealloc];
}

- (BOOL)canHandleAction:(id<STAction>)action withContext:(STActionContext *)context{
  return [self didChooseAction:action withContext:context shouldExecute:NO];
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
  // return YES;
  return [self handleSource:source withAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseAction:(id<STAction>)action withContext:(STActionContext *)context {
  [self didChooseAction:action withContext:context shouldExecute:YES];
}

- (BOOL)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
  NSMutableArray* validSources = [NSMutableArray array];
  if (action.sources) {
    for (id<STSource> source in action.sources) {
      if ([self canHandleSource:source forAction:action.type withContext:context]) {
        [validSources addObject:source];
      }
    }
    if (flag) {
      if ([validSources count] > 1) {
        STActionMenuFactory* factory = [[[STActionMenuFactory alloc] init] autorelease];
        NSOperation* operation = [factory createViewWithAction:action sources:validSources andContext:context forBlock:^(STViewCreator init) {
          if (init) {
            UIView* view = init(self);
            view.frame = [Util centeredAndBounded:view.frame.size inFrame:[[UIApplication sharedApplication] keyWindow].frame];
            [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.3]];
          }
        }];
        [self.operationQueue addOperation:operation];
      }
      else if ([validSources count] == 1) {
        [self handleSource:[validSources objectAtIndex:0] withAction:action.type withContext:context shouldExecute:YES];
      }
    }
  }
  return [validSources count] > 0;
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
  [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
  [self handleSource:source withAction:action withContext:context shouldExecute:YES];
}

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
  BOOL handled = FALSE;
  //if (flag) {
    NSLog(@"didChooseSource:%@:%@ forAction:%@", source.source, source.sourceID, action);
  //}
  id<STViewDelegate> sourceObject = [self.sources objectForKey:source.source];
  if (sourceObject != nil && 
      [sourceObject respondsToSelector:@selector(canHandleSource:forAction:withContext:)] &&
      [sourceObject canHandleSource:source forAction:action withContext:context] &&
      [sourceObject respondsToSelector:@selector(didChooseSource:forAction:withContext:)]) {
    handled = TRUE;
    if (flag) {
      [sourceObject didChooseSource:source forAction:action withContext:context];
    }
  }
  else if ([source.source isEqualToString:@"menu"]) {
    [Util globalLoadingLock];
    [[STStampedAPI sharedInstance] menuForEntityID:@"4e4c6fdd26f05a2b75000a75" andCallback:^(id<STMenu> menu) {
      [Util globalLoadingUnlock];
      if (menu && context.entityDetail) {
        UIView* popUp = [[[STMenuPopUp alloc] initWithEntityDetail:context.entityDetail andMenu:menu] autorelease];
        [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.75]];
      }
    }];
  }
  
  if (!handled && source.link) {
    handled = TRUE;
    if (flag) {
      [[UIApplication sharedApplication] openURL:[NSURL URLWithString:source.link]];
    }
  }
  return handled;
}

@end
