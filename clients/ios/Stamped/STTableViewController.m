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
  _tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, _headerHeight, 320, 363 - _headerHeight)];
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_tableView];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [_tableView release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
