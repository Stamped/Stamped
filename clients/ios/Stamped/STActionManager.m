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

@interface STActionManager () <STViewDelegate>

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;
- (BOOL)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;

@property (nonatomic, readonly, retain) NSOperationQueue* operationQueue;
@property (nonatomic, readonly, retain) NSMutableDictionary* sources;

@end

@implementation STActionManager

@synthesize operationQueue = _operationQueue;
@synthesize sources = _sources;

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
  }
  return self;
}

- (void)dealloc
{
  [_operationQueue release];
  [_sources release];
  [super dealloc];
}

- (BOOL)canHandleAction:(id<STAction>)action {
  return YES;
  //return [self didChooseAction:action shouldExecute:YES];
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
        NSOperation* operation = [factory createViewWithAction:action andSource:validSources forBlock:^(STViewCreator init) {
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
  id<STViewDelegate> sourceObject = [self.sources objectForKey:source.source];
  if (sourceObject != nil && [sourceObject canHandleSource:source forAction:action withContext:context]) {
    handled = TRUE;
    if (flag) {
      [sourceObject didChooseSource:source forAction:action withContext:context];
    }
  }
  else if ([action isEqualToString:@"phone"]) {
    if ([source.source isEqualToString:@"phone"] && source.sourceID != nil) {
      NSString* telURL = [NSString stringWithFormat:@"tel://%@",
                          [Util sanitizedPhoneNumberFromString:source.sourceID]];
      handled = TRUE;
      if (flag) {
        [[UIApplication sharedApplication] openURL:[NSURL URLWithString:telURL]];
      }
    }
  }
  else if ([source.source isEqualToString:@"menu"]) {
    NSOperation* operation = [[STMenuFactory sharedFactory] menuWithEntityId:@"4e4c6fdd26f05a2b75000a75" andCallbackBlock:^(id<STMenu> menu) {
      UIView* popUp = [[[STMenuPopUp alloc] initWithEntityDetail:context.entityDetail andMenu:menu] autorelease];
      [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.75]];
    }];
    [operation start];
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
