//
//  STActionMenuFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STViewDelegate.h"

@interface STActionMenuFactory : NSObject

- (NSOperation*)createWithAction:(id<STAction>)gallery forBlock:(void (^)(STViewCreator))callback;

@end
