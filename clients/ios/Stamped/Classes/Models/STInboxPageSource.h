//
//  STInboxPageSource.h
//  Stamped
//
//  Created by Landon Judkins on 5/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCache.h"
#import "STStampedAPI.h"

@interface STInboxPageSource : NSObject <STCachePageSource>

- (id)initWithScope:(STStampedAPIScope)scope;

@end
