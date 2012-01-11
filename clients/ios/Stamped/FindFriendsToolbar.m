//
//  FindFriendsToolbar.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "FindFriendsToolbar.h"

#import "UIButton+Stamped.h"

@implementation FindFriendsToolbar

@synthesize mainActionButton = mainActionButton_;
@synthesize previewButton = previewButton_;
@synthesize addEmailsButton = addEmailsButton_;
@synthesize centerButton = centerButton_;

- (void)commonInit {
  [super commonInit];
  mainActionButton_ = [UIButton stampedBlueButton];
  [self addSubview:mainActionButton_];
  mainActionButton_.hidden = YES;

  previewButton_ = [UIButton stampedToolbarButton];
  [self addSubview:previewButton_];
  previewButton_.hidden = YES;

  centerButton_ = [UIButton stampedBlueToolbarButton];
  [self addSubview:centerButton_];
  centerButton_.enabled = NO;

  addEmailsButton_ = [UIButton stampedToolbarButton];
  [self addSubview:addEmailsButton_];
  addEmailsButton_.hidden = YES;
}

- (void)dealloc {
  mainActionButton_ = nil;
  previewButton_ = nil;
  addEmailsButton_ = nil;
  centerButton_ = nil;
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

@end
