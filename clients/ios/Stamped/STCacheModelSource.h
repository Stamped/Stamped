//
//  STAbstractModelSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STModelSource.h"

@class STCacheModelSource;

@protocol STCacheModelSourceDelegate <NSObject>

- (void)objectForCache:(STCacheModelSource*)cache withKey:(NSString*)key andCurrentObject:(id)object withCallback:(void(^)(id))block;

@end

@interface STCacheModelSource : NSObject <STModelSource>

@property (nonatomic, readwrite, assign) id<STCacheModelSourceDelegate> delegate;

- (id)initWithMainKey:(NSString*)key;

- (void)setObject:(id)object forKey:(NSString*)key;

@end
