//
//  STDebug.h
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#include <string.h>
#import "STDebugDatum.h"

#define STLog(s) [[STDebug sharedInstance] log:[NSString stringWithFormat:@"%s:%d- %@", (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__), __LINE__, s]]

@interface STDebug : NSObject

- (void)log:(id)object;
+ (void)log:(id)object;
- (NSArray*)logSliceWithOffset:(NSInteger)offset andCount:(NSInteger)count;
- (STDebugDatum*)logItemAtIndex:(NSInteger)index;
- (NSInteger)logCount;

+ (STDebug*)sharedInstance;

@end
