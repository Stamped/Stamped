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
  STCacheModelSourceErrorNoDelegate,
} STCacheModelSourceError;

@class STCacheModelSource;

@protocol STCacheModelSourceDelegate <NSObject>
@required
- (STCancellation*)objectForCache:(STCacheModelSource*)cache 
                          withKey:(NSString*)key 
                 andCurrentObject:(id)object 
                     withCallback:(void(^)(id model, NSInteger cost, NSError* error, STCancellation* cancellation))block;
@end

@interface STCacheModelSource : NSObject <STModelSource>

@property (nonatomic, readwrite, assign) id<STCacheModelSourceDelegate> delegate;
@property (nonatomic, readwrite, assign) NSInteger maximumCost;

- (id)initWithDelegate:(id<STCacheModelSourceDelegate>)delegate;

- (void)setObject:(id)object forKey:(NSString*)key;
- (void)removeObjectForKey:(NSString*)key;

- (void)fastPurge;

+ (NSString*)errorDomain;

@end
