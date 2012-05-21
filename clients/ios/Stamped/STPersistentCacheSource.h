//
//  STAbstractModelSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STModelSource.h"

typedef enum {
  STPersistentCacheSourceErrorNoDelegate,
} STPersistentCacheSourceError;

@class STPersistentCacheSource;

@protocol STPersistentCacheSourceDelegate <NSObject>
@required
- (STCancellation*)objectForPersistentCache:(STPersistentCacheSource*)cache 
                                    withKey:(NSString*)key
                           andCurrentObject:(id)object 
                               withCallback:(void(^)(id<NSCoding> model, NSError* error, STCancellation* cancellation))block;
@end

@interface STPersistentCacheSource : NSObject <STModelSource>

@property (nonatomic, readwrite, assign) id<STPersistentCacheSourceDelegate> delegate;
@property (nonatomic, readwrite, assign) NSInteger maximumCost;
@property (nonatomic, readwrite, assign) NSNumber* maxAge;

- (id)initWithDelegate:(id<STPersistentCacheSourceDelegate>)delegate 
      andDirectoryPath:(NSString*)path 
    relativeToCacheDir:(BOOL)relative;

- (void)setObject:(id<NSCoding>)object forKey:(NSString*)key;

- (void)removeObjectForKey:(NSString*)key;

- (void)purgeOld;

- (void)purgeAll;

+ (NSString*)errorDomain;

@end
