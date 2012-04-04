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
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"

@interface STStampedAPI () <STCacheModelSourceDelegate>

@property (nonatomic, readonly, retain) STCacheModelSource* menuCache;
@property (nonatomic, readonly, retain) STCacheModelSource* stampCache;

@end

@implementation STStampedAPI

@synthesize menuCache = _menuCache;
@synthesize stampCache = _stampCache;

static STStampedAPI* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STStampedAPI alloc] init];
}

+ (STStampedAPI*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super init];
  if (self) {
    _menuCache = [[STCacheModelSource alloc] initWithMainKey:@"entityID" andDelegate:self];
    _stampCache = [[STCacheModelSource alloc] initWithMainKey:@"stampID" andDelegate:self];
  }
  return self;
}

- (void)stampForStampID:(NSString*)stampID andCallback:(void(^)(id<STStamp>))block {
  [self.stampCache fetchWithKey:stampID callback:block];
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
  [self.menuCache fetchWithKey:entityID callback:block];
}

- (void)objectForCache:(STCacheModelSource*)cache withKey:(NSString*)key andCurrentObject:(id)object withCallback:(void(^)(id))block {
  if (cache == self.menuCache) {
    [[STMenuFactory sharedFactory] menuWithEntityId:key andCallbackBlock:^(id<STMenu> menu) {
      block(menu);
    }];
  }
  else if (cache == self.stampCache) {
    NSDictionary* params = [NSDictionary dictionaryWithObject:key forKey:@"stamped_id"];
    NSString* path = @"/stamps/show.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path params:params mapping:[STSimpleStamp mapping] andCallback:^(NSArray* array, NSError* error) {
      id<STStamp> stamp = nil;
      if (array && [array count] > 0) {
        stamp = [array objectAtIndex:0];
      }
      block(stamp);
    }];
  }
}

@end
