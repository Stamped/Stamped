//
//  STReloadableTableViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STReloadableTableViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/RestKit.h>

#import "UIColor+Stamped.h"

static NSString* kPullDownText = @"Pull down to refresh...";
static NSString* kReleaseText = @"Release to refresh...";
static NSString* kLoadingText = @"Loading...";

@implementation STReloadableTableViewController

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  previousOffset_ = self.tableView.contentSize.height + self.tableView.contentOffset.y;

  reloadLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(87, -40, 146, 21)];
  reloadLabel_.text = kPullDownText;
  reloadLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  reloadLabel_.backgroundColor = [UIColor clearColor];
  reloadLabel_.textColor = [UIColor stampedGrayColor];
  reloadLabel_.textAlignment = UITextAlignmentCenter;
  [self.tableView addSubview:reloadLabel_];
  [reloadLabel_ release];
  
  arrowImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"refresh_arrow"]];
  arrowImageView_.frame = CGRectMake(60, -50, 18, 40);
  [self.tableView addSubview:arrowImageView_];
  [arrowImageView_ release];

  spinnerView_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
  spinnerView_.hidesWhenStopped = YES;
  spinnerView_.center = arrowImageView_.center;
  [self.tableView addSubview:spinnerView_];
  [spinnerView_ release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  reloadLabel_ = nil;
  arrowImageView_ = nil;
  spinnerView_ = nil;
}

- (void)dealloc {
  reloadLabel_ = nil;
  arrowImageView_ = nil;
  spinnerView_ = nil;
  [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Loader Methods.

- (void)setIsLoading:(BOOL)loading {
  if (isLoading_ == loading)
    return;
  
  isLoading_ = loading;
  shouldReload_ = NO;

  arrowImageView_.hidden = loading;
  if (loading) {
    [spinnerView_ startAnimating];
  } else {
    [spinnerView_ stopAnimating];
  }
  
  if (!loading) {
    reloadLabel_.text = kPullDownText;
    reloadLabel_.layer.transform = CATransform3DIdentity;
    [UIView animateWithDuration:0.2
                          delay:0
                        options:UIViewAnimationOptionBeginFromCurrentState | 
                                UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       self.tableView.contentInset = UIEdgeInsetsZero;
                     }
                     completion:nil];
    
    return;
  }

  reloadLabel_.text = kLoadingText;
  [UIView animateWithDuration:0.2
                        delay:0 
                      options:UIViewAnimationOptionBeginFromCurrentState | 
                              UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     self.tableView.contentInset = UIEdgeInsetsMake(70, 0, 0, 0);
                   }
                   completion:nil];
}

#pragma mark - To be implemented by subclasses.

- (void)userPulledToReload {}

- (void)reloadData {
  // NOTHING. YOU DO NOTHING!
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  scrollPosition_ = scrollView.contentOffset;
  if (isLoading_)
    return;
  
  shouldReload_ = scrollView.contentOffset.y < -65.0;
  reloadLabel_.text = shouldReload_ ? kReleaseText : kPullDownText;
  [UIView animateWithDuration:0.15
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | 
                              UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     CGAffineTransform transform = shouldReload_ ?
                         CGAffineTransformMakeRotation(M_PI) : CGAffineTransformIdentity;
                     arrowImageView_.transform = transform;
                   }
                   completion:nil];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  if (shouldReload_) {
    [self setIsLoading:YES];
    [self userPulledToReload];
  }
}

@end
