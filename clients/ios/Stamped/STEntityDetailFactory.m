//
//  STEntityDetailFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityDetailFactory.h"
#import <RestKit/RestKit.h>
#import "STSimpleEntityDetail.h"
#import "Util.h"
#import "STDebug.h"

//TODO deprecate

typedef void (^STEntityDetailFactoryCallback)(id<STEntityDetail>);

static STEntityDetailFactory* _sharedFactory = nil;
static NSString* const kEntityLookupPath = @"/entities/show.json";

@interface STEntityDetailFactory()

@property (nonatomic, retain) NSCache* entityCache;
@property (nonatomic, retain) NSCache* searchIDCache;

@end

@interface STEntityDetailFactoryHelper : NSObject <RKObjectLoaderDelegate>

@property (nonatomic, retain) STEntityDetailFactoryCallback callback;
@property (nonatomic, retain) NSString* searchID;

@end

@implementation STEntityDetailFactoryHelper

@synthesize callback = callback_;
@synthesize searchID = searchID_;

/*
 Dealloc verified: 23 03 2012
 */
- (void)dealloc {
  self.callback = nil;
  self.searchID = nil;
  [super dealloc];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [STDebug log:[NSString stringWithFormat:@"Entity detail failed to load from %@: %@", objectLoader.URL,error]];
  dispatch_async(dispatch_get_main_queue(), ^{
    @autoreleasepool {
      self.callback(nil);
      [self autorelease];
    }
  });
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  STSimpleEntityDetail* detail = [objects objectAtIndex:0];
  if (self.searchID) {
    [[STEntityDetailFactory sharedFactory].searchIDCache setObject:detail.entityID forKey:self.searchID];
  }
  [[STEntityDetailFactory sharedFactory].entityCache setObject:detail forKey:detail.entityID];
  dispatch_async(dispatch_get_main_queue(), ^{
    @autoreleasepool {
      self.callback(detail);
      [self autorelease];
    }
  });
}

@end

@implementation STEntityDetailFactory

@synthesize entityCache = entityCache_;
@synthesize searchIDCache = searchIDCache_;

#pragma mark - Public Methods.

- (id)init
{
  self = [super init];
  if (self) {
    self.entityCache = [[[NSCache alloc] init] autorelease];
    self.searchIDCache = [[[NSCache alloc] init] autorelease];
  }
  return self;
}

- (void)dealloc
{
  self.entityCache = nil;
  self.searchIDCache = nil;
  [super dealloc];
}

- (void)createWithParams:(NSDictionary*)params andCallbackBlock:(void (^)(id<STEntityDetail>))aBlock {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    aBlock(nil);
    return;
  }
  
  STEntityDetailFactoryHelper* helper = [[STEntityDetailFactoryHelper alloc] init];
  helper.callback = aBlock;
  helper.searchID = [params objectForKey:@"search_id"];
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:helper];
  
  objectLoader.objectMapping = [STSimpleEntityDetail mapping];
  
  objectLoader.params = params;
  
  [objectLoader send];
}


- (NSOperation*)entityDetailCreatorWithEntityId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STEntityDetail>))aBlock {
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
          id<STEntityDetail> cachedDetail = [self.entityCache objectForKey:anEntityID];
          cachedDetail = nil;
          if (cachedDetail) {
            dispatch_async(dispatch_get_main_queue(), ^{
              @autoreleasepool {
                NSLog(@"Used detail cache for %@",cachedDetail.title);
                aBlock(cachedDetail);
              }
            });
          }
          else {
            NSDictionary* params = [NSDictionary dictionaryWithObject:anEntityID forKey: @"entity_id"];
            [self createWithParams:params andCallbackBlock:aBlock];
          }
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

- (NSOperation*)entityDetailCreatorWithSearchId:(NSString*)aSearchID andCallbackBlock:(void (^)(id<STEntityDetail>))aBlock {
  __block NSBlockOperation* operation = [[[NSBlockOperation alloc] init] autorelease];
  [operation addExecutionBlock:^{
    @autoreleasepool {
      @try {
        if (aSearchID == nil) {
          dispatch_async(dispatch_get_main_queue(), ^{
            @autoreleasepool {
              aBlock(nil);
            }
          });
        }
        else {
          id<STEntityDetail> cachedDetail = nil;
          NSString* entityID = [self.searchIDCache objectForKey:aSearchID];
          if (entityID) {
            cachedDetail = [self.entityCache objectForKey:entityID];
          }
          if (cachedDetail) {
            dispatch_async(dispatch_get_main_queue(), ^{
              @autoreleasepool {
                NSLog(@"Used detail cache for %@",cachedDetail.title);
                aBlock(cachedDetail);
              }
            });
          }
          else {
            NSDictionary* params = [NSDictionary dictionaryWithObject:aSearchID forKey:@"search_id"];
            [self createWithParams:params andCallbackBlock:aBlock];
          }
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

+ (void)initialize {
  _sharedFactory = [[STEntityDetailFactory alloc] init];
}

+ (STEntityDetailFactory*)sharedFactory {
  return _sharedFactory;
}

@end
