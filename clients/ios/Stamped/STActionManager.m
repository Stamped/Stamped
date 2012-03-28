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
#import <StoreKit/StoreKit.h>

@interface STActionManager () <STViewDelegate, SKProductsRequestDelegate>

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action shouldExecute:(BOOL)flag;
- (BOOL)didChooseAction:(id<STAction>)action shouldExecute:(BOOL)flag;

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
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action {
 // return YES;
  return [self handleSource:source withAction:action shouldExecute:NO];
}

- (void)didChooseAction:(id<STAction>)action {
  [self didChooseAction:action shouldExecute:YES];
}

- (BOOL)didChooseAction:(id<STAction>)action shouldExecute:(BOOL)flag {
  NSMutableArray* validSources = [NSMutableArray array];
  if (action.sources) {
    for (id<STSource> source in action.sources) {
      if ([self canHandleSource:source forAction:action.type]) {
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
        [self handleSource:[validSources objectAtIndex:0] withAction:action.type shouldExecute:YES];
      }
    }
  }
  return [validSources count] > 0;
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action {
  [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
  [self handleSource:source withAction:action shouldExecute:YES];
}

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action shouldExecute:(BOOL)flag {
  BOOL handled = FALSE;
  id<STViewDelegate> sourceObject = [self.sources objectForKey:source.source];
  if (sourceObject != nil && [sourceObject canHandleSource:source forAction:action]) {
    handled = TRUE;
    if (flag) {
      [sourceObject didChooseSource:source forAction:action];
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
  else if ([source.source isEqualToString:@"itunes"]) {
    SKProductsRequest* request = [[SKProductsRequest alloc] initWithProductIdentifiers:[NSSet setWithObject:source.sourceID]];
    request.delegate = self;
    [request start];
  }
  
  if (!handled && source.link) {
    handled = TRUE;
    if (flag) {
      [[UIApplication sharedApplication] openURL:[NSURL URLWithString:source.link]];
    }
  }
  return handled;
}

- (void)productsRequest:(SKProductsRequest *)request didReceiveResponse:(SKProductsResponse *)response
{
  NSArray *myProducts = response.products;
  NSLog(@"%@",myProducts);
  // Populate your UI from the products list.
  // Save a reference to the products list.
}

@end
