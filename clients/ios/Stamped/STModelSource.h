//
//  STModelSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STModelSource <NSObject>

- (void)cacheWithKey:(NSString*)key callback:(void(^)(id))block;
- (void)updateWithKey:(NSString*)key callback:(void(^)(id))block;
- (void)fetchWithKey:(NSString*)key callback:(void(^)(id))block;

@end
