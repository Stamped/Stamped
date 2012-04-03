//
//  STRestKitLoader.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRestKitLoader.h"
#import "Util.h"

@interface STRestKitLoaderHelper : NSObject <RKObjectLoaderDelegate>

@property (nonatomic, copy) void(^callback)(NSArray*,NSError*);

@end

@implementation STRestKitLoaderHelper

@synthesize callback = _callback;

- (void)dealloc {
  [_callback release];
  [super dealloc];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [Util executeOnMainThread:^{
    self.callback(nil, error);
    [self autorelease];
  }];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  [Util executeOnMainThread:^{
    self.callback(objects, nil);
    [self autorelease];
  }];
}

@end

@implementation STRestKitLoader

static STRestKitLoader* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STRestKitLoader alloc] init];
}

+ (STRestKitLoader*)sharedInstance {
  return _sharedInstance;
}

- (void)loadWithPath:(NSString*)path 
              params:(NSDictionary*)params 
             mapping:(RKObjectMapping*)mapping 
         andCallback:(void(^)(NSArray*,NSError*))block {
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable ) {
    [Util executeOnMainThread:^{
      block(nil,nil);
    }];
    return;
  }

  STRestKitLoaderHelper* helper = [[STRestKitLoaderHelper alloc] init];
  helper.callback = block;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path
                                                                    delegate:helper];
  
  objectLoader.objectMapping = mapping;

  objectLoader.params = [params copy];

  [objectLoader send];
}

@end

