//
//  STStampFactory.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStamp.h"

@interface STStampFactory : NSObject

- (NSOperation*)stampWithStampId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STStamp>))aBlock;

+ (STStampFactory*)sharedInstance;

@end
