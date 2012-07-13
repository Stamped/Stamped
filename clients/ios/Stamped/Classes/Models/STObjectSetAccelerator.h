//
//  STObjectSetAccellerator.h
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCache.h"

@interface STObjectSetAccelerator : NSObject <STCacheAccelerator>

+ (id<STCacheAccelerator>)acceleratorForObjects:(NSArray<STDatum>*)objects;

@end
