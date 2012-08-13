//
//  STViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STViewController.h"
#import "Util.h"

@implementation STViewController

@synthesize shelfView = shelfView_;
@synthesize highlightView = highlightView_;

- (void)viewDidLoad {
  [super viewDidLoad];
  highlightView_ = [[UIView alloc] initWithFrame:CGRectMake(0, CGRectGetHeight(self.shelfView.frame) - 26, 320, 20)];
  highlightView_.backgroundColor = [UIColor colorWithRed:0.22 green:0.48 blue:0.85 alpha:1.0];
  highlightView_.alpha = 0;
  highlightView_.userInteractionEnabled = NO;
  [self.shelfView addSubview:highlightView_];
  [highlightView_ release];
}

- (UINavigationController*)navigationController {
  if ([super navigationController])
    return [super navigationController];
  
  return [Util currentNavigationController];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  CGRect shelfFrame = shelfView_.frame;
  shelfFrame.origin.y = MAX([self minimumShelfYPosition], [self maximumShelfYPosition] - scrollView.contentOffset.y);
  shelfView_.frame = shelfFrame;
  CGFloat yInset = CGRectGetMaxY(shelfFrame) - 9.0;
  if (self.navigationController.navigationBarHidden) {
    yInset -= 44;  // Height of the nav bar.
  }

  scrollView.scrollIndicatorInsets = UIEdgeInsetsMake(yInset, 0, 0, 0);
}

//TODO investigate value
- (CGFloat)minimumShelfYPosition {
  return -356;
}

//TODO investigate value
- (CGFloat)maximumShelfYPosition {
  return -356;
}

@end
