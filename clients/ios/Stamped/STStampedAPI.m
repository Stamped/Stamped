//
//  STStampedAPI.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedAPI.h"
#import "STMenuFactory.h"
#import "STEntityDetailFactory.h"
#import "Util.h"
#import "STCacheModelSource.h"

@interface STStampedAPI () <STCacheModelSourceDelegate>

@end

@implementation STStampedAPI

static STStampedAPI* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STStampedAPI alloc] init];
}

+ (STStampedAPI*)sharedInstance {
  return _sharedInstance;
}

- (void)entityForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntity>))block {
  [self entityDetailForEntityID:entityID andCallback:^(id<STEntityDetail> entityDetail) {
    block(entityDetail);
  }];
}

- (void)entityDetailForEntityID:(NSString*)entityID andCallback:(void(^)(id<STEntityDetail>))block {
  NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithEntityId:entityID andCallbackBlock:block];
  [Util runOperationAsynchronously:operation];
}

- (void)entityDetailForSearchID:(NSString*)searchID andCallback:(void(^)(id<STEntityDetail>))block{
  NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithSearchId:searchID andCallbackBlock:block];
  [Util runOperationAsynchronously:operation];
}

- (void)menuForEntityID:(NSString*)entityID andCallback:(void(^)(id<STMenu>))block {
  [[STMenuFactory sharedFactory] menuWithEntityId:entityID andCallbackBlock:^(id<STMenu> menu) {
    block(menu);
  }];
}

- (void)objectForCache:(STCacheModelSource*)cache withKey:(NSString*)key andCurrentObject:(id)object withCallback:(void(^)(id))block {
  
}

@end
