//
//  STContainerViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContainerViewController.h"
#import "STScrollViewContainer.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "Util.h"

static NSString* kPullDownText = @"Pull down to refresh...";
static NSString* kReleaseText = @"Release to refresh...";
static NSString* kLoadingText = @"Updating...";
static NSString* kNotConnectedText = @"Not connected to the Internet.";
static const CGFloat kReloadHeight = 60.0;

@interface STContainerViewController ()

@property (nonatomic, assign) BOOL disableReload;
@property (nonatomic, assign) BOOL shouldReload;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, readonly) UIView* shelfView;
@property (nonatomic, readonly) UILabel* reloadLabel;
@property (nonatomic, readonly) UILabel* lastUpdatedLabel;
@property (nonatomic, readonly) UIImageView* arrowImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* spinnerView;
@property (nonatomic, readwrite, retain) UIView* toolbarView;

- (void)userPulledToReload;
- (void)reloadData;
- (void)updateLastUpdatedTo:(NSDate*)date;

@end

@implementation STContainerViewController

@synthesize scrollView = _scrollView;
@synthesize disableReload = _disableReload;
@synthesize shouldReload = _shouldReload;
@synthesize loading = _loading;
@synthesize shelfView = _shelfView;
@synthesize reloadLabel = _reloadLabel;
@synthesize lastUpdatedLabel = _lastUpdatedLabel;
@synthesize arrowImageView = _arrowImageView;
@synthesize spinnerView = _spinnerView;
@synthesize toolbarView = _toolbarView;

- (id)init
{
  self = [super init];
  if (self) {
  }
  return self;
}

- (void)loadView {
  STScrollViewContainer* container = [[[STScrollViewContainer alloc] initWithDelegate:nil andFrame:CGRectMake(0, 0, 320, 420)] autorelease];
  CGFloat bottomPadding = 0;
  UIImageView* shelfBackground = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"shelf_background"]] autorelease];
  _shelfView = [[UIView alloc] initWithFrame:CGRectMake(0, -356, 320, 360)];
  [_shelfView addSubview:shelfBackground];
  
  
  _arrowImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"refresh_arrow"]];
  _arrowImageView.frame = CGRectMake(60, CGRectGetMaxY(_shelfView.bounds) - 58 - bottomPadding, 18, 40);
  [_shelfView addSubview:_arrowImageView];
  
  _spinnerView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
  _spinnerView.hidesWhenStopped = YES;
  _spinnerView.center = _arrowImageView.center;
  [_shelfView addSubview:_spinnerView];
  
  _reloadLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  _reloadLabel.text = kNotConnectedText;
  [_reloadLabel sizeToFit];
  _reloadLabel.frame = CGRectOffset(_reloadLabel.frame, 160 - CGRectGetWidth(_reloadLabel.frame) / 2, CGRectGetHeight(_shelfView.frame) - 57 - bottomPadding);
  _reloadLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  _reloadLabel.backgroundColor = [UIColor clearColor];
  _reloadLabel.textColor = [UIColor stampedGrayColor];
  _reloadLabel.textAlignment = UITextAlignmentCenter;
  [_shelfView addSubview:_reloadLabel];
  
  _lastUpdatedLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  _lastUpdatedLabel.text = @"Last updated a long time ago";
  [_lastUpdatedLabel sizeToFit];
  _lastUpdatedLabel.frame = CGRectOffset(_lastUpdatedLabel.frame, 160 - CGRectGetWidth(_lastUpdatedLabel.frame) / 2, CGRectGetHeight(self.shelfView.frame) - 41 - bottomPadding);
  _lastUpdatedLabel.font = [UIFont fontWithName:@"Helvetica" size:12];
  _lastUpdatedLabel.backgroundColor = [UIColor clearColor];
  _lastUpdatedLabel.textColor = [UIColor stampedLightGrayColor];
  _lastUpdatedLabel.textAlignment = UITextAlignmentCenter;
  [_shelfView addSubview:_lastUpdatedLabel];
  
  _scrollView = container;
  container.delegate = self;
  [container appendChildView:_shelfView];
  [container setScrollDelegate:self];
  UIView* mainView = [[[UIView alloc] initWithFrame:container.frame] autorelease];
  UIImageView* backgroundImage = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"gradient_background"]] autorelease];
  [mainView addSubview:backgroundImage];
  [mainView addSubview:container];
  self.view = mainView;
}

- (void)viewWillUnload {
  NSLog(@"warning SHOULD IMPLEMENT");
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UIScrollViewDelegate methods

//TODO investigate value
- (CGFloat)minimumShelfYPosition {
  return -356;
}

//TODO investigate value
- (CGFloat)maximumShelfYPosition {
  return -356;
}
- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  //CGRect shelfFrame = self.shelfView.frame;
  //shelfFrame.origin.y = MAX([self minimumShelfYPosition], [self maximumShelfYPosition] - scrollView.contentOffset.y);
  //self.shelfView.frame = shelfFrame;
  //CGFloat yInset = CGRectGetMaxY(shelfFrame) - 9.0;
  
  //scrollView.scrollIndicatorInsets = UIEdgeInsetsMake(yInset, 0, 0, 0);
  
  self.shouldReload = scrollView.contentOffset.y < -kReloadHeight;
  if (NO)
    self.reloadLabel.text = kNotConnectedText;
  else if (self.loading)
    self.reloadLabel.text = kLoadingText;
  else
    self.reloadLabel.text = self.shouldReload ? kReleaseText : kPullDownText;
  [UIView animateWithDuration:0.15
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     CGAffineTransform transform = _shouldReload ?
                     CGAffineTransformMakeRotation(M_PI) : CGAffineTransformIdentity;
                     _arrowImageView.transform = transform;
                     if ( !self.loading)
                       self.arrowImageView.alpha = 1.0;
                     if (NO)
                       self.arrowImageView.alpha = 0.0;
                   }
                   completion:nil];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  if (self.shouldReload) {
    self.loading = YES;
    [self userPulledToReload];
  }
}

- (void)updateLastUpdatedTo:(NSDate*)date {
  if (!date)
    return;
  
  self.lastUpdatedLabel.text = [NSString stringWithFormat:@"Last updated %@", [Util userReadableTimeSinceDate:date]];
  [self.lastUpdatedLabel setNeedsDisplay];
}


- (void)setLoading:(BOOL)loading {
  
  if (_loading == loading)
    return;  
  
  _loading = loading;
  _shouldReload = NO;
  
  if (loading)
    [_spinnerView startAnimating];
  else
    [_spinnerView stopAnimating];
  
  CGFloat bottomPadding = 0;
  
  if (!loading) {
    [UIView animateWithDuration:0.2
                          delay:0
                        options:UIViewAnimationOptionBeginFromCurrentState | 
     UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       CGRect reloadFrame = self.reloadLabel.frame;
                       reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 57 - bottomPadding;
                       self.reloadLabel.frame = reloadFrame;
                       if (NO) {
                         self.reloadLabel.text = kNotConnectedText;
                         self.arrowImageView.alpha = 0.0;
                       } else {
                         self.reloadLabel.text = kPullDownText;
                         self.arrowImageView.alpha = 1.0;
                       }
                       self.lastUpdatedLabel.alpha = 1.0;
                       self.scrollView.contentInset = UIEdgeInsetsZero;
                     }
                     completion:nil];
    
  }
  else {
    if (self.scrollView.contentOffset.y < 0) {
      [UIView animateWithDuration:0.2
                            delay:0 
                          options:UIViewAnimationOptionBeginFromCurrentState | 
       UIViewAnimationOptionAllowUserInteraction
                       animations:^{
                         CGRect reloadFrame = self.reloadLabel.frame;
                         reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 47 - bottomPadding;
                         self.reloadLabel.frame = reloadFrame;
                         if (NO)
                           self.reloadLabel.text = kNotConnectedText;
                         else 
                           self.reloadLabel.text = kLoadingText;
                         self.arrowImageView.alpha = 0.0;
                         self.lastUpdatedLabel.alpha = 0.0;
                         self.scrollView.contentInset = UIEdgeInsetsMake(kReloadHeight, 0, 0, 0);
                         self.arrowImageView.transform = CGAffineTransformIdentity;
                       }
                       completion:nil];
    } else {
      CGRect reloadFrame = self.reloadLabel.frame;
      reloadFrame.origin.y = CGRectGetHeight(self.shelfView.frame) - 47 - bottomPadding;
      self.reloadLabel.frame = reloadFrame;
      if (NO) {
        self.loading = NO;
      }
      else {
        self.reloadLabel.text = kLoadingText;
        self.arrowImageView.alpha = 0.0;
      }
      self.lastUpdatedLabel.alpha = 0.0;
    }
  }
}

#pragma mark - To be implemented by subclasses.

- (void)shouldFinishLoading {
  NSDate* now = [NSDate date];
  [self updateLastUpdatedTo:now];
  [self setLoading:NO];
}

- (void)userPulledToReload {
  [self reloadData];
}

- (void)reloadData {
  [self reloadStampedData];
  [self performSelector:@selector(shouldFinishLoading) withObject:nil afterDelay:.5];
}


- (void)setToolbar:(UIView*)view withAnimation:(BOOL)animated {
  self.toolbarView = view;
  [Util reframeView:view withDeltas:CGRectMake(0, CGRectGetMaxY(self.scrollView.frame), 0, 0)];
  [self.view addSubview:view];
  void (^block)(void)  = ^{
    [Util reframeView:view withDeltas:CGRectMake(0, -view.frame.size.height, 0, 0)];
    [Util reframeView:self.scrollView withDeltas:CGRectMake(0, 0, 0, -view.frame.size.height)];
  };
  if (animated) {
    [UIView animateWithDuration:.25 animations:block];
  }
  else {
    block();
  }
}

- (void)reloadStampedData {
  for (id view in self.view.subviews) {
    if ([view respondsToSelector:@selector(reloadStampedData)]) {
      [view reloadStampedData];
    }
  }
}


#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  CGFloat delta = -216;
  if (self.toolbarView) {
    delta += self.toolbarView.frame.size.height;
  }
  CGRect scrollFrame = self.scrollView.frame;
  scrollFrame.size.height += delta;
  
  CGRect relativeFrame = [Util relativeFrameForView:textField inAncestorView:self.scrollView];
  CGFloat contentY = self.scrollView.contentOffset.y;
  if (relativeFrame.size.height < scrollFrame.size.height) {
    contentY = CGRectGetMaxY(relativeFrame) - scrollFrame.size.height;
  }
  else {
    contentY = relativeFrame.origin.y;
  }
  NSLog(@"scrolled to compensate by %f", contentY - self.scrollView.contentOffset.y);
  [UIView animateWithDuration:0.3
                        delay:0.0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     self.scrollView.frame = scrollFrame;
                     self.scrollView.contentOffset = CGPointMake(self.scrollView.contentOffset.x, contentY);
                   }
                   completion:nil];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  CGFloat delta = 216;
  if (self.toolbarView) {
    delta -= self.toolbarView.frame.size.height;
  }
  [UIView animateWithDuration:0.3
                        delay:0.0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     [Util reframeView:self.scrollView withDeltas:CGRectMake(0, 0, 0, delta)];
                   }
                   completion:nil];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}


@end
