//
//  STMenuFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMenuFactory.h"
#import "Util.h"
#import "STSimpleMenu.h"
#import <RestKit/RestKit.h>

static NSString* const kMenuLookupPath = @"/entities/menu.json";


@interface STMenuFactoryHelper : NSObject <RKObjectLoaderDelegate>

@property (nonatomic, retain) void(^callback)(id<STMenu>);

@end

@implementation STMenuFactoryHelper

@synthesize callback = _callback;

- (void)dealloc {
  [_callback release];
  [super dealloc];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  dispatch_async(dispatch_get_main_queue(), ^{
    @autoreleasepool {
      self.callback(nil);
      [self autorelease];
    }
  });
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  STSimpleMenu* menu = [objects objectAtIndex:0];
  dispatch_async(dispatch_get_main_queue(), ^{
    @autoreleasepool {
      self.callback(menu);
      [self autorelease];
    }
  });
}

@end


@implementation STMenuFactory

static STMenuFactory* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STMenuFactory alloc] init];
}

- (void)createWithParams:(NSDictionary*)params andCallbackBlock:(void (^)(id<STMenu>))aBlock {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    aBlock(nil);
    return;
  }
  
  STMenuFactoryHelper* helper = [[STMenuFactoryHelper alloc] init];
  helper.callback = aBlock;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kMenuLookupPath
                                                                    delegate:helper];
  
  objectLoader.objectMapping = [STSimpleMenu mapping];
  
  objectLoader.params = params;
  
  [objectLoader send];
}

- (NSOperation*)menuWithEntityId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STMenu>))aBlock {
  __block NSBlockOperation* operation = [[[NSBlockOperation alloc] init] autorelease];
  [operation addExecutionBlock:^{
    @autoreleasepool {
      @try {
        if (anEntityID == nil) {
          dispatch_async(dispatch_get_main_queue(), ^{
            @autoreleasepool {
              aBlock(nil);
            }
          });
        }
        else {
          NSDictionary* params = [NSDictionary dictionaryWithObject:anEntityID forKey: @"entity_id"];
          [self createWithParams:params andCallbackBlock:aBlock];
        }
      }
      @catch (NSException *exception) {
        [Util logOperationException:exception withMessage:nil];
        dispatch_async(dispatch_get_main_queue(), ^{
          @autoreleasepool {
            aBlock(nil);
          }
        });
      }
      @finally {
      }
    }
  }];
  return operation;
}

+ (STMenuFactory*)sharedFactory {
  return _sharedInstance;
}

@end
