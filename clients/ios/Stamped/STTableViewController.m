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

- (id)initWithHeaderHeight:(CGFloat)height
{
  self = [super init];
  if (self) {
    _headerHeight = height;
  }
  return self;
}

- (void)dealloc
{
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  CGFloat deltaHeight = -_headerHeight;
  if (self.toolbar) {
    deltaHeight -= self.toolbar.frame.size.height;
  }
  _tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, _headerHeight, 320, 416 + deltaHeight)];
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_tableView];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [_tableView release];
}

- (UITableView *)tableView {
  [self view];
  return _tableView;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  NSIndexPath* path = [self.tableView indexPathForSelectedRow];
  if (path) {
    NSLog(@"deselect");
    [self.tableView deselectRowAtIndexPath:path animated:YES];
  }
}

@end
