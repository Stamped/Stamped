//
//  STInboxViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContainerViewController.h"
#import "STTableViewController.h"

@interface STInboxViewController : STTableViewController

- (void)newStampCreated:(id<STStamp>)stamp;

+ (STInboxViewController*)sharedInstance;

@end
