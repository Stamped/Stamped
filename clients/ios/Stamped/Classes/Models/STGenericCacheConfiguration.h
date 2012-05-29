//
//  STGenericCacheConfiguration.h
//  Stamped
//
//  Created by Landon Judkins on 5/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCache.h"

@interface STGenericCacheConfiguration : NSObject <STCacheConfiguration>

@property (nonatomic, readwrite, retain) id<STCachePageSource> pageSource;
@property (nonatomic, readwrite, copy) NSURL* directory;
@property (nonatomic, readwrite, assign) NSTimeInterval pageFaultAge;
@property (nonatomic, readwrite, assign) NSInteger preferredPageSize;
@property (nonatomic, readwrite, assign) NSInteger minimumPageSize;

@end
