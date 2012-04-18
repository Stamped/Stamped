//
//  STTableViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContainerViewController.h"

@interface STTableViewController : STContainerViewController

- (id)initWithHeaderHeight:(CGFloat)height;

@property (nonatomic, readonly, retain) UITableView* tableView;

@end
