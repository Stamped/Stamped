//
//  STClosableOverlayView.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STClosableOverlayView.h"

typedef void(^OnCloseBlock)(void);

@interface STClosableOverlayView ()
- (void)closeButtonPressed:(id)sender;
- (void)runCloseBlock;

@property (nonatomic, readonly) UIImageView* topRibbonView;
@property (nonatomic, readonly) UIImageView* bottomRibbonView;
@property (nonatomic, readonly) UIButton* closeButton;
@property (nonatomic, copy) OnCloseBlock closeBlock;
@end

@implementation STClosableOverlayView

@synthesize contentView = contentView_;
@synthesize topRibbonView = topRibbonView_;
@synthesize bottomRibbonView = bottomRibbonView_;
@synthesize closeButton = closeButton_;
@synthesize closeBlock = closeBlock_;

- (id)init {
  UIWindow* window = [[UIApplication sharedApplication] delegate].window;
  self = [super initWithFrame:window.frame];
  if (self) {
    self.alpha = 0;
    self.backgroundColor = [UIColor clearColor];
    UIView* black = [[UIView alloc] initWithFrame:self.bounds];
    black.backgroundColor = [UIColor blackColor];
    black.alpha = 0.75;
    [self addSubview:black];
    [black release];
    [window addSubview:self];
    contentView_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 290, 200)];
    contentView_.backgroundColor = [UIColor whiteColor];
    contentView_.center = black.center;
    [self addSubview:contentView_];
    [contentView_ release];
    
    topRibbonView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_top"]];
    [contentView_ addSubview:topRibbonView_];
    [topRibbonView_ release];

    bottomRibbonView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_bot"]];
    [contentView_ addSubview:bottomRibbonView_];
    [bottomRibbonView_ release];
    
    closeButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    closeButton_.alpha = 0;
    UIImage* buttonImage = [UIImage imageNamed:@"popup_wht_closeButton"];
    [closeButton_ setImage:buttonImage forState:UIControlStateNormal];
    closeButton_.bounds = CGRectMake(0, 0, buttonImage.size.width, buttonImage.size.height);
    [closeButton_ addTarget:self action:@selector(closeButtonPressed:) forControlEvents:UIControlEventTouchUpInside];
    [self addSubview:closeButton_];
  }
  return self;
}

- (void)dealloc {
  contentView_ = nil;
  topRibbonView_ = nil;
  bottomRibbonView_ = nil;
  self.closeBlock = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  CGFloat maxHeight = 0.0;
  for (UIView* view in contentView_.subviews)
    maxHeight = MAX(maxHeight, CGRectGetHeight(view.frame));

  CGRect rect = contentView_.bounds;
  rect.size.height = maxHeight + CGRectGetHeight(topRibbonView_.bounds) + CGRectGetHeight(bottomRibbonView_.bounds);
  contentView_.bounds = rect;
  
  for (UIView* view in contentView_.subviews) {
    if (view == topRibbonView_ || view == bottomRibbonView_)
      continue;

    view.center = CGPointMake(CGRectGetMidX(contentView_.bounds), CGRectGetMidY(contentView_.bounds));
  }
  
  rect = closeButton_.frame;
  rect.origin.x = CGRectGetMinX(contentView_.frame) - (CGRectGetWidth(closeButton_.bounds) / 2);
  rect.origin.y = CGRectGetMinY(contentView_.frame) - (CGRectGetHeight(closeButton_.bounds) / 2) + 2;
  closeButton_.frame = rect;
  
  rect = bottomRibbonView_.frame;
  rect.origin.y = CGRectGetMaxY(contentView_.bounds) - CGRectGetHeight(bottomRibbonView_.bounds);
  bottomRibbonView_.frame = rect;
}

- (void)show {
  contentView_.alpha = 0;
  contentView_.transform = CGAffineTransformMakeScale(0.75, 0.75);
  [UIView animateWithDuration:0.4 animations:^{
    self.alpha = 1.0;
  } completion:^(BOOL finished) {
    [UIView animateWithDuration:0.2 animations:^{
      contentView_.alpha = 1.0;
      contentView_.transform = CGAffineTransformMakeScale(1.02, 1.02);
    } completion:^(BOOL finished) {
      [UIView animateWithDuration:0.2 animations:^{
        contentView_.transform = CGAffineTransformMakeScale(0.98, 0.98);
      } completion:^(BOOL finished) {
        [UIView animateWithDuration:0.2 animations:^{
          contentView_.transform = CGAffineTransformIdentity;
        } completion:^(BOOL finished) {
          [UIView animateWithDuration:0.4 animations:^{
            closeButton_.alpha = 1.0;
          }];
        }];
      }];
    }];
  }];
}

- (void)showWithOnCloseHandler:(void (^)(void))block {
  [self show];
}

- (void)runCloseBlock {
  if (self.closeBlock)
    [self closeBlock]();
}

- (void)closeButtonPressed:(id)sender {
  [UIView animateWithDuration:0.3 animations:^{
    self.alpha = 0;
  } completion:^(BOOL finished) {
    [self removeFromSuperview];
    [self performSelectorOnMainThread:@selector(runCloseBlock) withObject:nil waitUntilDone:NO];
  }];
}

@end
