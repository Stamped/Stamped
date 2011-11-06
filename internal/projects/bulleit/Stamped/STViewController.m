//
//  STViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STViewController.h"

@interface STViewController ()
@property (nonatomic, assign) CGFloat initialShelfYPosition;
@end

@implementation STViewController

@synthesize shelfView = shelfView_;
@synthesize initialShelfYPosition = initialShelfYPosition_;

- (void)viewDidLoad {
  [super viewDidLoad];
  initialShelfYPosition_ = shelfView_.frame.origin.y;
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  CGRect shelfFrame = shelfView_.frame;
  shelfFrame.origin.y = MAX(-356, initialShelfYPosition_ - scrollView.contentOffset.y);
  shelfView_.frame = shelfFrame;
  scrollView.scrollIndicatorInsets = UIEdgeInsetsMake(CGRectGetMaxY(shelfFrame) - 9.0, 0, 0, 0);
}

@end
