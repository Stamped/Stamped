//
//  STPersistentCacheSource.m
//  Stamped
//
//  Created by Landon Judkins on 5/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPersistentCacheSource.h"
#import "Util.h"

@interface STPersistentCacheSource()

@property (nonatomic, readonly, copy) NSString* path;

@end

@implementation STPersistentCacheSource

@synthesize delegate = delegate_;
@synthesize maxAge = maxAge_;
@synthesize maximumCost = maximumCost_;
@synthesize path = path_;

+ (NSString*)_fullPathWithBase:(NSString*)path andKey:(NSString*)key {
  return [NSString stringWithFormat:@"%@/%@", path, key];
}

- (NSString*)fullPathForKey:(NSString*)key {
  return [STPersistentCacheSource _fullPathWithBase:self.path andKey:key];
}

- (BOOL)writeObject:(id<NSCoding>)object withKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  if (![[NSFileManager defaultManager] fileExistsAtPath:self.path]) {
    [[NSFileManager defaultManager] createDirectoryAtPath:self.path withIntermediateDirectories:YES attributes:nil error:nil];
  }
  return [NSKeyedArchiver archiveRootObject:object toFile:fullPath];
}

- (id<NSCoding>)readObjectForKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  return [NSKeyedUnarchiver unarchiveObjectWithFile:fullPath];
}

- (NSNumber*)ageForKey:(NSString*)key {
  NSString* fullPath = [self fullPathForKey:key];
  if (![[NSFileManager defaultManager] fileExistsAtPath:fullPath]) {
    return nil;
  }
  return [NSNumber numberWithInteger:[[[[NSFileManager defaultManager] attributesOfItemAtPath:fullPath error:nil] fileModificationDate] timeIntervalSinceNow]];
}

- (BOOL)isFresh:(NSString*)key {
  NSNumber* age = [self ageForKey:key];
  if (!self.maxAge) {
    return YES;
  }
  if (age && age.doubleValue < self.maxAge.doubleValue) {
    return YES;
  }
  return NO;
}

- (id)initWithDelegate:(id<STPersistentCacheSourceDelegate>)delegate 
      andDirectoryPath:(NSString*)path 
    relativeToCacheDir:(BOOL)relative {
  self = [super init];
  if (self) {
    if (relative) {
      NSArray* paths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
      NSString* cacheDir = [paths objectAtIndex:0];
      path = [NSString stringWithFormat:@"%@/%@", cacheDir, path];
    }
    path_ = [path copy];
    maximumCost_ = NSIntegerMax;
    maxAge_ = nil;
    delegate_ = delegate;
  }
  return self;
}

- (void)dealloc
{
  [path_ release];
  [maxAge_ release];
  [super dealloc];
}

- (void)setObject:(id<NSCoding>)object forKey:(NSString*)key {
  [self writeObject:object withKey:key];
}

- (void)removeObjectForKey:(NSString*)key {
  NSString* fullPath = [STPersistentCacheSource _fullPathWithBase:self.path andKey:key];
  [[NSFileManager defaultManager] removeItemAtPath:fullPath error:nil];
}

- (void)purgeOld {
  NSNumber* maxAge = self.maxAge;
  if (maxAge) {
    NSArray* keys = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:self.path error:nil];
    if (keys) {
      for (NSString* key in keys) {
        NSNumber* age = [self ageForKey:key];
        if (!age || age.doubleValue > maxAge.doubleValue) {
          [[NSFileManager defaultManager] removeItemAtPath:[self fullPathForKey:key] error:nil];
        }
      }
    }
  }
}

- (void)purgeAll {
  [[NSFileManager defaultManager] removeItemAtPath:self.path error:nil];
}

+ (NSString*)errorDomain {
  return @"STPersistenCacheSource";
}

- (STCancellation*)cacheWithKey:(NSString*)key callback:(void(^)(id, NSError*, STCancellation*))block {
  return [self fetchWithKey:key callback:block];
}

- (STCancellation*)updateWithKey:(NSString*)key callback:(void(^)(id, NSError*, STCancellation*))block {
  id object = [self cachedValueForKey:key];
  id<STPersistentCacheSourceDelegate> delegate = self.delegate;
  if (delegate) {
    STCancellation* cancellation = [delegate objectForPersistentCache:self 
                                                              withKey:key 
                                                     andCurrentObject:object 
                                                         withCallback:^(id<NSCoding> model, NSError* error, STCancellation* cancellation2) {
                                                           if (model) {
                                                             [self writeObject:model withKey:key];
                                                           }
                                                           if (!cancellation2.cancelled) {
                                                             block(model, error, cancellation2);
                                                           }
                                                         }];
    return cancellation;
  }
  else {
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(nil, [NSError errorWithDomain:[STPersistentCacheSource errorDomain] 
                                       code:STPersistentCacheSourceErrorNoDelegate 
                                   userInfo:[NSDictionary dictionary]], cancellation);
      }
    }];
    return cancellation;
  }
}

- (STCancellation*)fetchWithKey:(NSString*)key callback:(void(^)(id model, NSError* error, STCancellation* cancellation))block {
  if ([self isFresh:key]) {
    id object = [self cachedValueForKey:key];
    if (object) {
      STCancellation* cancellation = [STCancellation cancellation];
      [Util executeOnMainThread:^{
        if (!cancellation.cancelled) {
          block(object, nil, cancellation);
        }
      }];
      return cancellation;
    }
  }
  return [self updateWithKey:key callback:block];
}

- (id)cachedValueForKey:(NSString*)key {
  return [self readObjectForKey:key];
}

@end
