//
//  STMenuFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STMenu.h"

@interface STMenuFactory : NSObject

- (NSOperation*)menuWithEntityId:(NSString*)entityID andCallbackBlock:(void (^)(id<STMenu>))aBlock;

+ (STMenuFactory*)sharedFactory;

@end
