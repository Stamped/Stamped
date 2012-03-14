//
//  STActionsViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"
#import "STViewDelegate.h"

@interface STActionsViewFactory : NSObject

- (void)createWithActions:(NSArray<STAction>*)actions
                 delegate:(id<STViewDelegate>)delegate
                withLabel:(id)label;

@end
