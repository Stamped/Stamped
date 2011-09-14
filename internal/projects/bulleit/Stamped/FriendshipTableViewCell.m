//
//  FriendshipTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/13/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "FriendshipTableViewCell.h"

@implementation FriendshipTableViewCell

@synthesize indicator = indicator_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    self.disclosureArrowHidden = YES;
    indicator_ = [[UIActivityIndicatorView alloc]
        initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    indicator_.hidesWhenStopped = YES;
    [customView_ addSubview:indicator_];
    [indicator_ release];
    
    followButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    [followButton_ setImage:[UIImage imageNamed:@"add_friends_follow_button"]
                   forState:UIControlStateNormal];
    followButton_.frame = CGRectMake(320 - 54 - 5, 10, 54, 30);
    [customView_ addSubview:followButton_];
    
    unfollowButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    [unfollowButton_ setImage:[UIImage imageNamed:@"add_friends_unfollow_button"]
                     forState:UIControlStateNormal];
    unfollowButton_.frame = CGRectMake(320 - 66 - 5, 10, 66, 30);
    [customView_ addSubview:unfollowButton_];
  }
  return self;
}

@end
