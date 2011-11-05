//
//  STTableViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

@implementation STTableViewController

@synthesize tableView = tableView_;
@synthesize shelfImageView = shelfImageView_;

#pragma mark - UIScrollViewDelegate methods.

- (void)dealloc {
  self.tableView = nil;
  self.shelfImageView = nil;
  [super dealloc];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.tableView = nil;
  self.shelfImageView = nil;
}

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  CGRect shelfFrame = shelfImageView_.frame;
  shelfFrame.origin.y = MAX(-356, -356 - scrollView.contentOffset.y);
  shelfImageView_.frame = shelfFrame;
}

@end
