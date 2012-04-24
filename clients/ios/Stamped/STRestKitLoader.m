//
//  STRestKitLoader.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRestKitLoader.h"
#import "Util.h"
#import "AccountManager.h"
#import "STDebug.h"

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
  [STDebug log:[NSString stringWithFormat:@"RestKit: Failed request with %d:\n%@\n%@ ", objectLoader.response.statusCode, objectLoader.URL, objectLoader.params]];
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];
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

@interface STRestKitLoaderBooleanHelper : NSObject <RKRequestDelegate>

@property (nonatomic, copy) void(^callback)(BOOL,NSError*);

@end

@implementation STRestKitLoaderBooleanHelper

@synthesize callback = _callback;

- (void)dealloc {
  [_callback release];
  [super dealloc];
}

#pragma mark - RKRequestDelegate methods

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  [STDebug log:[NSString stringWithFormat:@"RestKit: Failed request:\n%@\n%@ ", request.URL, request.params]];
  //TODO handle bad token
  //if ()
  //  [[AccountManager sharedManager] refreshToken];
  [Util executeOnMainThread:^{
    self.callback(NO, error);
    [self autorelease];
  }];
}

- (void)request:(RKRequest *)request didLoadResponse:(RKResponse *)response {
  [Util executeOnMainThread:^{
    BOOL result = [response.bodyAsString isEqualToString:@"true"];
    self.callback(result, nil);
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
                post:(BOOL)post
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
  if (post) {
    objectLoader.method = RKRequestMethodPOST;
  }
  
  objectLoader.objectMapping = mapping;

  objectLoader.params = [params copy];

  [objectLoader send];
}


- (void)loadOneWithPath:(NSString*)path 
                   post:(BOOL)post
                 params:(NSDictionary*)params 
                mapping:(RKObjectMapping*)mapping 
            andCallback:(void(^)(id,NSError*))block {
  [self loadWithPath:path post:post params:params mapping:mapping andCallback:^(NSArray* array, NSError* error) {
    id result = nil;
    if (array && [array count] > 0) {
      result = [array objectAtIndex:0];
    }
    block(result, error);
  }];
}

- (void)booleanWithPath:(NSString*)path
                   post:(BOOL)post
                 params:(NSDictionary*)params
            andCallback:(void(^)(BOOL boolean, NSError* error))block {
  STRestKitLoaderBooleanHelper* helper = [[STRestKitLoaderBooleanHelper alloc] init];
  helper.callback = block;
  
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:path delegate:helper]; 
  if (post) {
    request.method = RKRequestMethodPOST;
  }
  request.params = params;
  [request send];
}

@end

