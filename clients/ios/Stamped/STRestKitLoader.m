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

@interface STRestKitLoaderHelper : NSObject <RKObjectLoaderDelegate, STCancellationDelegate>

- (id)initWithCallback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readonly, copy) void(^callback)(NSArray*,NSError*,STCancellation*);
@property (nonatomic, readonly, retain) STCancellation* cancellation;

@end

@implementation STRestKitLoaderHelper

@synthesize callback = callback_;
@synthesize cancellation = cancellation_;

- (id)initWithCallback:(void(^)(NSArray* array, NSError* error, STCancellation* cancellation))block
{
  self = [super init];
  if (self) {
    [self retain];
    callback_ = [block copy];
    cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
  }
  return self;
}

- (void)dealloc {
  [callback_ release];
  [cancellation_ release];
  [super dealloc];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
  //NSLog(@"Cancelled operation");
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [self autorelease];
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSAssert1(!self.cancellation.cancelled, @"should have cancelled loader %@", self);
  [STDebug log:[NSString stringWithFormat:@"RestKit: Failed request with %d:\n%@\n%@ ", objectLoader.response.statusCode, objectLoader.URL, objectLoader.params]];
  if ([self.cancellation finish]) {
    if ([objectLoader.response isUnauthorized])
      [[AccountManager sharedManager] refreshToken];
    [Util executeOnMainThread:^{
      self.callback(nil, error, self.cancellation);
      [self autorelease];
    }];
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSAssert1(!self.cancellation.cancelled, @"should have cancelled loader %@", self);
  //NSLog(@"RestKit Loaded %d objects for %@",objects.count, objectLoader.URL);
  if ([self.cancellation finish]) {
    [Util executeOnMainThread:^{
      self.callback(objects, nil, self.cancellation);
      [self autorelease];
    }];
  }
}

@end

@interface STRestKitLoaderBooleanHelper : NSObject <RKRequestDelegate, STCancellationDelegate>

- (id)initWithCallback:(void(^)(BOOL result, NSError* error, STCancellation* cancellation))block;

@property (nonatomic, readonly, copy) void(^callback)(BOOL result, NSError* error, STCancellation* cancellation);
@property (nonatomic, readonly, retain) STCancellation* cancellation;


@end

@implementation STRestKitLoaderBooleanHelper

@synthesize callback = callback_;
@synthesize cancellation = cancellation_;

- (id)initWithCallback:(void(^)(BOOL result, NSError* error, STCancellation* cancellation))block {
  self = [super init];
  if (self) {
    [self retain];
    callback_ = [block copy];
    cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
  }
  return self;
}

- (void)dealloc {
  [callback_ release];
  [cancellation_ release];
  [super dealloc];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
  //NSLog(@"Cancelled operation");
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [self autorelease];
}

#pragma mark - RKRequestDelegate methods

- (void)request:(RKRequest*)request didFailLoadWithError:(NSError*)error {
  NSAssert1(!self.cancellation.cancelled, @"should have cancelled loader %@", self);
  [STDebug log:[NSString stringWithFormat:@"RestKit: Failed request:\n%@\n%@ ", request.URL, request.params]];
  if ([self.cancellation finish]) {
    //TODO handle bad token
    //if ()
    //  [[AccountManager sharedManager] refreshToken];
    [Util executeOnMainThread:^{
      self.callback(NO, error, self.cancellation);
      [self autorelease];
    }];
  }
}

- (void)request:(RKRequest *)request didLoadResponse:(RKResponse *)response {
  NSAssert1(!self.cancellation.cancelled, @"should have cancelled loader %@", self);
  if ([self.cancellation finish]) {
    [Util executeOnMainThread:^{
      BOOL result = [response.bodyAsString isEqualToString:@"true"];
      self.callback(result, nil, self.cancellation);
      [self autorelease];
    }];
  }
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


- (STCancellation*)loadWithURL:(NSString*)url 
                          post:(BOOL)post
                        params:(NSDictionary*)params 
                       mapping:(RKObjectMapping*)mapping 
                   andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable ) {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(nil, nil, cancellation);
        cancellation.delegate = nil;
      }
    }];
    return cancellation;
  }
  else {
    STRestKitLoaderHelper* helper = [[[STRestKitLoaderHelper alloc] initWithCallback:block] autorelease];    
    RKObjectManager* objectManager = [RKObjectManager sharedManager];
    
    //RestKit full path workaround
    RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:@"dummyValue"
                                                                      delegate:helper];
    [objectLoader setURL:[RKURL URLWithBaseURLString:[NSString stringWithFormat:@"%@",url] resourcePath:@""]];
    //[objectLoader setURL:[RKURL URLWithString:[NSString stringWithFormat:@"https://dev.stamped.com/v0%@",path]]];
    //NSLog(@"URL:%@, %@",objectLoader.URL, objectLoader.URL.class);
    if (post) {
      objectLoader.method = RKRequestMethodPOST;
    }
    
    objectLoader.objectMapping = mapping;
    
    objectLoader.params = [[params copy] autorelease];
    
    [objectLoader send];
    STCancellation* can = [[helper.cancellation retain] autorelease];
    can.decoration = [NSString stringWithFormat:@"RestKit:%@ %@", objectLoader.resourcePath, objectLoader.params];
    return can;
  }
}

- (STCancellation*)loadOneWithURL:(NSString*)url
                             post:(BOOL)post
                           params:(NSDictionary*)params 
                          mapping:(RKObjectMapping*)mapping 
                      andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block {
  return [self loadWithURL:url
                      post:post 
                    params:params 
                   mapping:mapping 
               andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                 id result = nil;
                 if (array && [array count] > 0) {
                   result = [array objectAtIndex:0];
                 }
                 block(result, error, cancellation);
               }];
}

- (STCancellation*)booleanWithURL:(NSString*)url
                             post:(BOOL)post
                           params:(NSDictionary*)params
                      andCallback:(void(^)(BOOL boolean, NSError* error, STCancellation* cancellation))block {
  STRestKitLoaderBooleanHelper* helper = [[[STRestKitLoaderBooleanHelper alloc] initWithCallback:block] autorelease];
  
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:@"dummyValue" delegate:helper]; 
  [request setURL:[RKURL URLWithBaseURLString:[NSString stringWithFormat:@"%@",url] resourcePath:@""]];
  if (post) {
    request.method = RKRequestMethodPOST;
  }
  request.params = [[params copy] autorelease];
  [request send];
  
  return [[helper.cancellation retain] autorelease];
}

- (STCancellation*)loadWithPath:(NSString*)path 
                           post:(BOOL)post
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable ) {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(nil, nil, cancellation);
        cancellation.delegate = nil;
      }
    }];
    return cancellation;
  }
  else {
    STRestKitLoaderHelper* helper = [[[STRestKitLoaderHelper alloc] initWithCallback:block] autorelease];    
    RKObjectManager* objectManager = [RKObjectManager sharedManager];
    RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path
                                                                      delegate:helper];
    if (post) {
      objectLoader.method = RKRequestMethodPOST;
    }
    
    objectLoader.objectMapping = mapping;
    
    objectLoader.params = [[params copy] autorelease];
    
   // NSLog(@"RestKit:%@-%@",path, params);
    
    [objectLoader send];
    STCancellation* can = [[helper.cancellation retain] autorelease];
    can.decoration = [NSString stringWithFormat:@"RestKit:%@ %@", objectLoader.resourcePath, objectLoader.params];
    return can;
  }
}

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block {
  return [self loadWithPath:path 
                       post:post 
                     params:params 
                    mapping:mapping 
                andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
                  id result = nil;
                  if (array && [array count] > 0) {
                    result = [array objectAtIndex:0];
                  }
                  block(result, error, cancellation);
                }];
}

- (STCancellation*)booleanWithPath:(NSString*)path
                              post:(BOOL)post
                            params:(NSDictionary*)params
                       andCallback:(void(^)(BOOL boolean, NSError* error, STCancellation* cancellation))block {
  STRestKitLoaderBooleanHelper* helper = [[[STRestKitLoaderBooleanHelper alloc] initWithCallback:block] autorelease];
  
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:path delegate:helper]; 
  if (post) {
    request.method = RKRequestMethodPOST;
  }
  request.params = [[params copy] autorelease];
  [request send];
  
  return [[helper.cancellation retain] autorelease];
}

@end

