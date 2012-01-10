//
//  FriendshipTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/13/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "FriendshipTableViewCell.h"

#import "UIButton+Stamped.h"

@implementation FriendshipTableViewCell

@synthesize indicator = indicator_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    self.disclosureArrowImageView.hidden = YES;
    indicator_ = [[UIActivityIndicatorView alloc]
        initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    indicator_.hidesWhenStopped = YES;
    [self.contentView addSubview:indicator_];
    [indicator_ release];
    
    followButton_ = [UIButton stampedFollowButton];
    [followButton_ sizeToFit];
    followButton_.frame = CGRectMake(320 - CGRectGetWidth(followButton_.frame) - 35, 10,
                                     CGRectGetWidth(followButton_.frame) + 30, 29);
    [self.contentView addSubview:followButton_];
    
    unfollowButton_ = [UIButton stampedFollowingButton];
    [unfollowButton_ sizeToFit];
    unfollowButton_.frame = CGRectMake(320 - CGRectGetWidth(unfollowButton_.frame) - 20, 10,
                                       CGRectGetWidth(unfollowButton_.frame) + 15, 29);
    [self.contentView addSubview:unfollowButton_];
  }
  return self;
}

- (void)dealloc {
  indicator_ = nil;
  followButton_ = nil;
  unfollowButton_ = nil;
  [super dealloc];
}

@end
