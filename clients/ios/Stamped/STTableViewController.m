//
//  STStampsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

@interface STTableViewController ()

@property (nonatomic, readonly, assign) CGFloat headerHeight;

@end

@implementation STTableViewController

@synthesize tableView = _tableView;
@synthesize headerHeight = _headerHeight;

- (id)initWithHeaderHeight:(CGFloat)height {
  if ((self = [super init])) {
    _headerHeight = height;
  }
  return self;
}

- (void)dealloc {
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  CGFloat deltaHeight = self.view.bounds.size.height-_headerHeight;
  if (self.toolbar) {
    deltaHeight -= self.toolbar.frame.size.height;
  }
  _tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, _headerHeight, 320, deltaHeight)];
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_tableView];
    
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [_tableView release];
}

- (UITableView *)tableView {
  [self view];
  return _tableView;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
}

@end
