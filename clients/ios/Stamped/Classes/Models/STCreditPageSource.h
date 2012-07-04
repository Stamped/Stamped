//
//  STCreditPageSource.h
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STCache.h"

@interface STCreditPageSource : NSObject <STCachePageSource>

- (id)initWithUserID:(NSString*)userID;

@end
