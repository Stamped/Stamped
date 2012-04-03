//
//  STStandardViewController.h
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STViewDelegate.h"
#import "STScrollViewContainer.h"
#import "STTableViewController.h"
#import <RestKit/RestKit.h>

@interface STStandardViewController : STTableViewController


@property (nonatomic, readonly, retain) UIView* shelfView;

@end
