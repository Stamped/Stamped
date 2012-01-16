//
//  FindFriendsToolbar.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "FindFriendsToolbar.h"

#import "UIButton+Stamped.h"

@interface FindFriendsToolbar ()
- (void)buttonPressed:(id)sender;
@end

@implementation FindFriendsToolbar

@synthesize mainActionButton = mainActionButton_;
@synthesize previewButton = previewButton_;
@synthesize addEmailsButton = addEmailsButton_;
@synthesize centerButton = centerButton_;
@synthesize inviteMode = inviteMode_;
@synthesize delegate = delegate_;

- (void)commonInit {
  [super commonInit];
  mainActionButton_ = [UIButton stampedBlueButton];
  [self addSubview:mainActionButton_];
  mainActionButton_.alpha = 0;
  mainActionButton_.enabled = NO;

  previewButton_ = [UIButton stampedToolbarButton];
  [previewButton_ setTitle:@"Preview" forState:UIControlStateNormal];
  [self addSubview:previewButton_];
  previewButton_.alpha = 0;
  previewButton_.enabled = NO;

  centerButton_ = [UIButton stampedBlueToolbarButton];
  [self addSubview:centerButton_];
  centerButton_.enabled = NO;

  addEmailsButton_ = [UIButton stampedToolbarButton];
  [self addSubview:addEmailsButton_];
  addEmailsButton_.alpha = 0;

  for (UIButton* b in [NSArray arrayWithObjects:mainActionButton_, previewButton_, centerButton_, addEmailsButton_, nil])
    [b addTarget:self action:@selector(buttonPressed:) forControlEvents:UIControlEventTouchUpInside];
}

- (void)dealloc {
  mainActionButton_ = nil;
  previewButton_ = nil;
  addEmailsButton_ = nil;
  centerButton_ = nil;
  delegate_ = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  [mainActionButton_ sizeToFit];
  CGFloat width = CGRectGetWidth(mainActionButton_.frame) + 15;
  mainActionButton_.frame =
      CGRectMake(320 - width - 10, 10, width, 29);

  [previewButton_ sizeToFit];
  width = CGRectGetWidth(previewButton_.frame) + 15;
  previewButton_.frame = CGRectMake(10, 10, width, 29);

  [centerButton_ sizeToFit];
  width = CGRectGetWidth(centerButton_.frame) + 15;
  centerButton_.frame = CGRectMake(160 - ceilf(width / 2), 10, width, 29);
}

- (void)setInviteMode:(BOOL)inviteMode {
  if (inviteMode != inviteMode_)
    inviteMode_ = inviteMode;
  
  [UIView animateWithDuration:0.2
                        delay:0
                      options:(UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState)
                   animations:^{
                     centerButton_.alpha = inviteMode ? 0.0 : 1.0;
                     previewButton_.alpha = inviteMode ? 1.0 : 0.0;
                     mainActionButton_.alpha = inviteMode ? 1.0 : 0.0;
                   }
                   completion:nil];
}

#pragma mark - Private methods.

- (void)buttonPressed:(id)sender {
  if (sender == centerButton_) {
    [delegate_ toolbar:self centerButtonPressed:centerButton_];
  } else if (sender == previewButton_) {
    [delegate_ toolbar:self previewButtonPressed:previewButton_];
  } else if (sender == mainActionButton_) {
    [delegate_ toolbar:self mainActionButtonPressed:mainActionButton_];
  }
}

@end
