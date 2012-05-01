//
//  STModelSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCancellation.h"

@protocol STModelSource <NSObject>

- (STCancellation*)cacheWithKey:(NSString*)key callback:(void(^)(id model, NSError* error, STCancellation* cancellation))block;
- (STCancellation*)updateWithKey:(NSString*)key callback:(void(^)(id model, NSError* error, STCancellation* cancellation))block;
- (STCancellation*)fetchWithKey:(NSString*)key callback:(void(^)(id model, NSError* error, STCancellation* cancellation))block;
- (id)cachedValueForKey:(NSString*)key;

@end
