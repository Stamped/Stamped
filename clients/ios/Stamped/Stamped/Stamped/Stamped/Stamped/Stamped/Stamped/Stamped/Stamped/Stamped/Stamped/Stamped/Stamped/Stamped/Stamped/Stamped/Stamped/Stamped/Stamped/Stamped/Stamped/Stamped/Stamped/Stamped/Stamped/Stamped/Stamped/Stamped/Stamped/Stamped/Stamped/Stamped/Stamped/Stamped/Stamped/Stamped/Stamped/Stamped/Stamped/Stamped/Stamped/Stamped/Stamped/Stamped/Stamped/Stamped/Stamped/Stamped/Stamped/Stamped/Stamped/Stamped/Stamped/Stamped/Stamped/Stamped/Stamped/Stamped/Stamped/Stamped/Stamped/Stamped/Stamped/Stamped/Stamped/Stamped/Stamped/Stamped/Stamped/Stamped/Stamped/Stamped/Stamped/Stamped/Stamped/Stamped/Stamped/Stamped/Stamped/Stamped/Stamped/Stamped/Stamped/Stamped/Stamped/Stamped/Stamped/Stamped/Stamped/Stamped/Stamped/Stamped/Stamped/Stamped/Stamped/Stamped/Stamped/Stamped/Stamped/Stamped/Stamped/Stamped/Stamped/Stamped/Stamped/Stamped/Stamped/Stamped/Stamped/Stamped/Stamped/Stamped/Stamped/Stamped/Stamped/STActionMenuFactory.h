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

- (NSOperation*)createViewWithAction:(id<STAction>)action 
                             sources:(NSArray*)sources 
                          andContext:(STActionContext*)context 
                            forBlock:(void (^)(STViewCreator))callback;

@end
