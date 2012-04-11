//
//  STRootMenuView.h
//  Stamped
//
//  Created by Landon Judkins on 4/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"

@interface STRootMenuView : STViewContainer

- (void)toggle;

+ (STRootMenuView*)sharedInstance;

@end
