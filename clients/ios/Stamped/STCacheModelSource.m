//
//  STAbstractModelSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCacheModelSource.h"
#import "Util.h"

@interface STCacheModelSource ()

@property (nonatomic, readonly, copy) NSString* mainKey;
@property (nonatomic, readonly, retain) NSCache* cache;

@end

@implementation STCacheModelSource

@synthesize delegate = _delegate;
@synthesize mainKey = _mainKey;
@synthesize cache = _cache;

- (id)initWithMainKey:(NSString*)key andDelegate:(id<STCacheModelSourceDelegate>)delegate {
  self = [super init];
  if (self) {
    _mainKey = [key copy];
    _cache = [[NSCache alloc] init];
    _delegate = delegate;
  }
  return self;
}

- (void)setObject:(id)object forKey:(NSString*)key {
  [_cache setObject:object forKey:key];
}

- (void)cacheWithKey:(NSString*)key callback:(void(^)(id))block {
  [self fetchWithKey:key callback:block];
}

- (void)updateWithKey:(NSString*)key callback:(void(^)(id))block {
  id object = [self.cache objectForKey:key];
  id<STCacheModelSourceDelegate> delegate = self.delegate;
  [Util executeAsync:^{
    if (delegate) {
      [delegate objectForCache:self withKey:key andCurrentObject:object withCallback:^(id result) {
        if (result) {
          [self.cache setObject:result forKey:key];
        }
        [Util executeOnMainThread:^{
          block(result);
        }];
      }];
    }
    else {
      [Util executeOnMainThread:^{
        block(nil);
      }];
    }
  }];
}

- (void)fetchWithKey:(NSString*)key callback:(void(^)(id))block {
  id object = [self.cache objectForKey:key];
  if (object) {
    [Util executeOnMainThread:^{
      block(object);
    }];
  }
  else {
    [self updateWithKey:key callback:block];
  }
}

@end
