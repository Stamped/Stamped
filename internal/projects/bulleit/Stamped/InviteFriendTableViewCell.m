//
//  InviteFriendTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/6/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "InviteFriendTableViewCell.h"

#import "UIColor+Stamped.h"
#import "UserImageView.h"

static const CGFloat kUserImageSize = 41.0;

@implementation InviteFriendTableViewCell

@synthesize userImageView = userImageView_;
@synthesize emailLabel = emailLabel_;
@synthesize nameLabel = nameLabel_;
@synthesize inviteButton = inviteButton_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [self initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(10, 5, kUserImageSize, kUserImageSize)];
    [self addSubview:userImageView_];
    [userImageView_ release];

    nameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(userImageView_.frame) + 16, 8, 181, 21)];
    nameLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    nameLabel_.highlightedTextColor = [UIColor whiteColor];
    nameLabel_.textColor = [UIColor stampedBlackColor];
    nameLabel_.backgroundColor = [UIColor clearColor];
    [self.contentView addSubview:nameLabel_];
    [nameLabel_ release];
    
    emailLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(nameLabel_.frame), 27, 181, 17)];
    emailLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    emailLabel_.backgroundColor = [UIColor clearColor];
    emailLabel_.textColor = [UIColor stampedLightGrayColor];
    emailLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:emailLabel_];
    [emailLabel_ release];
    
    inviteButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    [inviteButton_ setImage:[UIImage imageNamed:@"invite_button"]
                   forState:UIControlStateNormal];
    [inviteButton_ setImage:[UIImage imageNamed:@"invited_button"]
                   forState:UIControlStateDisabled];
    inviteButton_.frame = CGRectMake(320 - 54 - 5, 10, 54, 30);
    [self.contentView addSubview:inviteButton_];
  }
  return self;
}

@end
