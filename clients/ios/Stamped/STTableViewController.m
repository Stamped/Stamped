//
//  STTableViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/RestKit.h>

#import "STSearchField.h"
#import "Util.h"
#import "UIColor+Stamped.h"

static NSString* kPullDownText = @"Pull down to refresh...";
static NSString* kReleaseText = @"Release to refresh...";
static NSString* kLoadingText = @"Updating...";
static NSString* kNotConnectedText = @"Not connected to the Internet.";
static const CGFloat kReloadHeight = 60.0;

@interface STTableViewController ()
- (void)setOverlayHidden:(BOOL)hidden;
- (void)overlayTapped:(UITapGestureRecognizer*)recognizer;
@end

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
@synthesize searchOverlay = searchOverlay_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;

#pragma mark - UIScrollViewDelegate methods.

- (void)dealloc {
  self.tableView = nil;
  self.shelfView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
  self.searchOverlay = nil;
  self.searchField = nil;
  self.cancelButton = nil;
  reloadLabel_ = nil;
  lastUpdatedLabel_ = nil;
  arrowImageView_ = nil;
  spinnerView_ = nil;
  [super dealloc];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.tableView = nil;
  self.shelfView = nil;
  self.stampFilterBar.delegate = nil;
  self.stampFilterBar = nil;
  self.searchOverlay = nil;
  self.searchField = nil;
  self.cancelButton = nil;
  reloadLabel_ = nil;
  lastUpdatedLabel_ = nil;
  arrowImageView_ = nil;
  spinnerView_ = nil;
}

- (void)viewDidLoad {
  [super viewDidLoad];

  CGFloat bottomPadding = 0;
  if (stampFilterBar_ || searchField_) {
    bottomPadding = 46;

    searchOverlay_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 480)];
    searchOverlay_.backgroundColor = [UIColor blackColor];
    searchOverlay_.alpha = 0;
    UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                                 action:@selector(overlayTapped:)];
    [searchOverlay_ addGestureRecognizer:recognizer];
    [recognizer release];
    [self.view insertSubview:searchOverlay_ belowSubview:self.shelfView];
  }

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
    reloadLabel_.text = kNotConnectedText;
    [reloadLabel_ sizeToFit];
    reloadLabel_.frame = CGRectOffset(reloadLabel_.frame, 160 - CGRectGetWidth(reloadLabel_.frame) / 2, CGRectGetHeight(self.shelfView.frame) - 57 - bottomPadding);
    reloadLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    reloadLabel_.backgroundColor = [UIColor clearColor];
    reloadLabel_.textColor = [UIColor stampedGrayColor];
    reloadLabel_.textAlignment = UITextAlignmentCenter;
    [self.shelfView addSubview:reloadLabel_];
    [reloadLabel_ release];
    
    lastUpdatedLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    lastUpdatedLabel_.text = @"Last updated a long time ago";
    [lastUpdatedLabel_ sizeToFit];
    lastUpdatedLabel_.frame = CGRectOffset(lastUpdatedLabel_.frame, 160 - CGRectGetWidth(lastUpdatedLabel_.frame) / 2, CGRectGetHeight(self.shelfView.frame) - 41 - bottomPadding);
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

- (void)overlayTapped:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  if (stampFilterBar_)
    [stampFilterBar_.searchField resignFirstResponder];

  if (searchField_)
    [searchField_ resignFirstResponder];
}

- (void)setIsLoading:(BOOL)loading {
  if (disableReload_)
    return;
  
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    loading = NO;
  
  if (isLoading_ == loading)
    return;  
  
  isLoading_ = loading;
  shouldReload_ = NO;

  if (loading )
    [spinnerView_ startAnimating];
  else
    [spinnerView_ stopAnimating];
  
  CGFloat bottomPadding = 0;
  if (stampFilterBar_ || searchField_)
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
                       RKClient* client = [RKClient sharedClient];
                       if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
                         reloadLabel_.text = kNotConnectedText;
                         arrowImageView_.alpha = 0.0;
                       } else {
                         reloadLabel_.text = kPullDownText;
                         arrowImageView_.alpha = 1.0;
                       }
                       lastUpdatedLabel_.alpha = 1.0;
                       self.tableView.contentInset = UIEdgeInsetsZero;
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
                       RKClient* client = [RKClient sharedClient];
                       if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
                         reloadLabel_.text = kNotConnectedText;
                       else 
                         reloadLabel_.text = kLoadingText;
                       arrowImageView_.alpha = 0.0;
                       lastUpdatedLabel_.alpha = 0.0;
                       self.tableView.contentInset = UIEdgeInsetsMake(kReloadHeight, 0, 0, 0);
                       arrowImageView_.transform = CGAffineTransformIdentity;
                     }
                     completion:nil];
  } else {
    CGRect reloadFrame = reloadLabel_.frame;
    reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 47 - bottomPadding;
    reloadLabel_.frame = reloadFrame;
    RKClient* client = [RKClient sharedClient];
    if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
      self.isLoading = NO;
    }
    else {
      reloadLabel_.text = kLoadingText;
      arrowImageView_.alpha = 0.0;
    }
    lastUpdatedLabel_.alpha = 0.0;
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
  
  RKClient* client = [RKClient sharedClient];
  if (isLoading_ && client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    self.isLoading = NO;
  
  if (isLoading_ || disableReload_)
    return;
  
  shouldReload_ = scrollView.contentOffset.y < -kReloadHeight;
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
    reloadLabel_.text = kNotConnectedText;
  else
    reloadLabel_.text = shouldReload_ ? kReleaseText : kPullDownText;
  [UIView animateWithDuration:0.15
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     CGAffineTransform transform = shouldReload_ ?
                         CGAffineTransformMakeRotation(M_PI) : CGAffineTransformIdentity;
                     arrowImageView_.transform = transform;
                     RKClient* client = [RKClient sharedClient];
                     if (client.reachabilityObserver.isReachabilityDetermined && client.isNetworkReachable && !isLoading_)
                       arrowImageView_.alpha = 1.0;
                     if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable)
                       arrowImageView_.alpha = 0.0;
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

- (void)stampFilterBarSearchFieldDidBeginEditing {
  [self setOverlayHidden:NO];
}

- (void)stampFilterBarSearchFieldDidEndEditing {
  [self setOverlayHidden:YES];
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  if ((STSearchField*)textField != searchField_)
    return;

  if (!searchField_.text.length) {
    [self setIsLoading:NO];
    CGFloat offset = (CGRectGetWidth(cancelButton_.frame) + 5) * -1;
    cancelButton_.alpha = 1;
    [UIView animateWithDuration:0.2 animations:^{
      cancelButton_.frame = CGRectOffset(cancelButton_.frame, offset, 0);
      CGRect frame = searchField_.frame;
      frame.size.width += offset;
      searchField_.frame = frame;
    }];
    disableReload_ = YES;
  }
  [self setOverlayHidden:NO];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  if ((STSearchField*)textField != searchField_)
    return;

  if (!searchField_.text.length) {
    CGFloat offset = CGRectGetWidth(cancelButton_.frame) + 5;
    [UIView animateWithDuration:0.2 animations:^{
      cancelButton_.frame = CGRectOffset(cancelButton_.frame, offset, 0);
      CGRect frame = searchField_.frame;
      frame.size.width += offset;
      searchField_.frame = frame;
    } completion:^(BOOL finished) {
      cancelButton_.alpha = 0;
      disableReload_ = NO;
    }];
  }
  [self setOverlayHidden:YES];
}

- (void)setOverlayHidden:(BOOL)hidden {
  if (hidden) {
    [UIView animateWithDuration:0.3 animations:^{
      searchOverlay_.alpha = 0;
    } completion:^(BOOL finished) {
      self.tableView.scrollEnabled = YES;
    }];
  } else {
    [self.tableView setContentOffset:CGPointZero animated:YES];
    self.tableView.scrollEnabled = NO;
    [UIView animateWithDuration:0.3 animations:^{
      searchOverlay_.alpha = 0.75;
    }];
  }
}

- (CGFloat)maximumShelfYPosition {
  if (searchField_ || stampFilterBar_)
    return -312;

  return [super maximumShelfYPosition];
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  disableReload_ = NO;
  searchField_.text = nil;
  if ([searchField_ isFirstResponder])
    [searchField_ resignFirstResponder];
  else
    [self textFieldDidEndEditing:searchField_];
}

#pragma mark - To be implemented by subclasses.

- (void)userPulledToReload {}

- (void)reloadData {}

- (void)updateLastUpdatedTo:(NSDate*)date {
  if (!date)
    return;

  lastUpdatedLabel_.text = [NSString stringWithFormat:@"Last updated %@", [Util userReadableTimeSinceDate:date]];
  [lastUpdatedLabel_ setNeedsDisplay];
}

@end
