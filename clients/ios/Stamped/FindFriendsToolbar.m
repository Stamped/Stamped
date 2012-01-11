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
@synthesize inviteButton = inviteButton_;

- (void)commonInit {
  [super commonInit];
  mainActionButton_ = [UIButton stampedBlueButton];
  [self addSubview:mainActionButton_];
}

- (void)dealloc {
  mainActionButton_ = nil;
  previewButton_ = nil;
  inviteButton_ = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  [mainActionButton_ sizeToFit];
  mainActionButton_.frame =
      CGRectMake(320 - CGRectGetWidth(mainActionButton_.frame) - 20, 10,
                 CGRectGetWidth(mainActionButton_.frame) + 15, 29);
}

@end
