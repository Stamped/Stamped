//
//  STTableViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Util.h"
#import "UIColor+Stamped.h"

static NSString* kPullDownText = @"Pull down to refresh...";
static NSString* kReleaseText = @"Release to refresh...";
static NSString* kLoadingText = @"Updating...";
static const CGFloat kReloadHeight = 60.0;

@implementation STTableViewController

@synthesize tableView = tableView_;
@synthesize stampFilterBar = stampFilterBar_;
@synthesize shouldReload = shouldReload_;
@synthesize disableReload = disableReload_;
@synthesize hasHeaders = hasHeaders_;
@synthesize isLoading = isLoading_;
@synthesize reloadLabel = reloadLabel_;
@synthesize lastUpdatedLabel = lastUpdatedLabel_;
@synthesize arrowImageView = arrowImageView_;
@synthesize spinnerView = spinnerView_;
@synthesize hideWhenEmpty = hideWhenEmpty_;

#pragma mark - UIScrollViewDelegate methods.

- (void)dealloc {
  self.tableView = nil;
  self.shelfView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
  [super dealloc];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.tableView = nil;
  self.shelfView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
}

- (void)viewDidLoad {
  [super viewDidLoad];

  CGFloat bottomPadding = 0;
  if (stampFilterBar_)
    bottomPadding = 46;

  if (!disableReload_) {
    arrowImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"refresh_arrow"]];
    arrowImageView_.frame = CGRectMake(60, CGRectGetMaxY(self.shelfView.bounds) - 58 - bottomPadding, 18, 40);
    [self.shelfView addSubview:arrowImageView_];
    [arrowImageView_ release];

    spinnerView_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    spinnerView_.hidesWhenStopped = YES;
    spinnerView_.center = arrowImageView_.center;
    [self.shelfView addSubview:spinnerView_];
    [spinnerView_ release];
    
    reloadLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    reloadLabel_.text = kPullDownText;
    [reloadLabel_ sizeToFit];
    reloadLabel_.frame = CGRectOffset(reloadLabel_.frame, 78, CGRectGetHeight(self.shelfView.frame) - 57 - bottomPadding);
    reloadLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    reloadLabel_.backgroundColor = [UIColor clearColor];
    reloadLabel_.textColor = [UIColor stampedGrayColor];
    reloadLabel_.textAlignment = UITextAlignmentCenter;
    [self.shelfView addSubview:reloadLabel_];
    [reloadLabel_ release];
    
    lastUpdatedLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    lastUpdatedLabel_.text = @"Last updated a long time ago";
    [lastUpdatedLabel_ sizeToFit];
    lastUpdatedLabel_.frame = CGRectOffset(lastUpdatedLabel_.frame, 49, CGRectGetHeight(self.shelfView.frame) - 41 - bottomPadding);
    lastUpdatedLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    lastUpdatedLabel_.backgroundColor = [UIColor clearColor];
    lastUpdatedLabel_.textColor = [UIColor stampedLightGrayColor];
    lastUpdatedLabel_.textAlignment = UITextAlignmentCenter;
    [self.shelfView addSubview:lastUpdatedLabel_];
    [lastUpdatedLabel_ release];
  }
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
}

- (void)setIsLoading:(BOOL)loading {
  if (isLoading_ == loading || disableReload_)
    return;

  isLoading_ = loading;
  shouldReload_ = NO;

  if (loading)
    [spinnerView_ startAnimating];
  else
    [spinnerView_ stopAnimating];
  
  CGFloat bottomPadding = 0;
  if (stampFilterBar_)
    bottomPadding = 46;
  
  if (!loading) {
    [UIView animateWithDuration:0.2
                          delay:0
                        options:UIViewAnimationOptionBeginFromCurrentState | 
                                UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       CGRect reloadFrame = reloadLabel_.frame;
                       reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 57 - bottomPadding;
                       reloadLabel_.frame = reloadFrame;
                       reloadLabel_.text = kPullDownText;
                       lastUpdatedLabel_.alpha = 1.0;
                       self.tableView.contentInset = UIEdgeInsetsZero;
                       arrowImageView_.alpha = 1.0;
                     }
                     completion:nil];
    
    return;
  }
  
  if (self.tableView.contentOffset.y < 0) {
    [UIView animateWithDuration:0.2
                          delay:0 
                        options:UIViewAnimationOptionBeginFromCurrentState | 
                                UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       CGRect reloadFrame = reloadLabel_.frame;
                       reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 47 - bottomPadding;
                       reloadLabel_.frame = reloadFrame;
                       reloadLabel_.text = kLoadingText;
                       lastUpdatedLabel_.alpha = 0.0;
                       self.tableView.contentInset = UIEdgeInsetsMake(kReloadHeight, 0, 0, 0);
                       arrowImageView_.alpha = 0.0;
                       arrowImageView_.transform = CGAffineTransformIdentity;
                     }
                     completion:nil];
  } else {
    CGRect reloadFrame = reloadLabel_.frame;
    reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 47 - bottomPadding;
    reloadLabel_.frame = reloadFrame;
    reloadLabel_.text = kLoadingText;
    lastUpdatedLabel_.alpha = 0.0;
    arrowImageView_.alpha = 0.0;
  }
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  [super scrollViewDidScroll:scrollView];

  if (isLoading_ && hasHeaders_) {
    if (scrollView.contentOffset.y >= 0)
      scrollView.contentInset = UIEdgeInsetsZero;
    else
      scrollView.contentInset = UIEdgeInsetsMake(MIN(-scrollView.contentOffset.y, kReloadHeight), 0, 0, 0);
  }

  if (stampFilterBar_ && (stampFilterBar_.searchQuery.length > 0 || stampFilterBar_.filterType != StampFilterTypeNone)) {
    self.highlightView.alpha = MIN(1.0, (15 + (-self.shelfView.frame.origin.y - 356)) / 15);
  }
  
  if (isLoading_ || disableReload_)
    return;
  
  shouldReload_ = scrollView.contentOffset.y < -kReloadHeight;
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

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
              andQuery:(NSString*)query {}

#pragma mark - To be implemented by subclasses.

- (void)userPulledToReload {}

- (void)reloadData {}

- (void)reloadTableData {
  [self.tableView reloadData];
  if (hideWhenEmpty_) {
    BOOL hidden = [self.tableView numberOfRowsInSection:0] == 0;
    self.tableView.hidden = hidden;
    self.shelfView.hidden = hidden;
  }
}

- (void)updateLastUpdatedTo:(NSDate*)date {
  lastUpdatedLabel_.text = [NSString stringWithFormat:@"Last updated %@", [Util userReadableTimeSinceDate:date]];
}

@end
