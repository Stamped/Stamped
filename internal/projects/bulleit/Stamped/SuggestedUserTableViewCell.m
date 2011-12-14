//
//  SuggestedUserTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/30/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "SuggestedUserTableViewCell.h"

#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "User.h"
#import "Util.h"

static const CGFloat kUserImageSize = 50.0;

@interface SuggestedUserTableViewCell ()
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) UILabel* fullNameLabel;
@property (nonatomic, readonly) UILabel* usernameLabel;
@property (nonatomic, readonly) UILabel* locationLabel;

@end

@implementation SuggestedUserTableViewCell

@synthesize user = user_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;
@synthesize userImageView = userImageView_;
@synthesize stampImageView = stampImageView_;
@synthesize fullNameLabel = fullNameLabel_;
@synthesize usernameLabel = usernameLabel_;
@synthesize locationLabel = locationLabel_;
@synthesize bioLabel = bioLabel_;
@synthesize indicator = indicator_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [self initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    self.clipsToBounds = YES;

    indicator_ = [[UIActivityIndicatorView alloc]
                  initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    indicator_.hidesWhenStopped = YES;
    [self.contentView addSubview:indicator_];
    [indicator_ release];

    userImageView_ = [[UserImageView alloc]
        initWithFrame:CGRectMake(10, 10, kUserImageSize, kUserImageSize)];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];
    
    stampImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(userImageView_.frame) - 23, -13, 46, 46)];
    [self.contentView addSubview:stampImageView_];
    [stampImageView_ release];
    
    fullNameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(userImageView_.frame) + 8, 8, 181, 21)];
    fullNameLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    fullNameLabel_.highlightedTextColor = [UIColor whiteColor];
    fullNameLabel_.textColor = [UIColor stampedBlackColor];
    fullNameLabel_.backgroundColor = [UIColor clearColor];
    [self.contentView addSubview:fullNameLabel_];
    [fullNameLabel_ release];
    
    usernameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(fullNameLabel_.frame), 28, 181, 17)];
    usernameLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    usernameLabel_.backgroundColor = [UIColor clearColor];
    usernameLabel_.textColor = [UIColor stampedLightGrayColor];
    usernameLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:usernameLabel_];
    [usernameLabel_ release];
    
    locationLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(fullNameLabel_.frame), 44, 181, 17)];
    locationLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    locationLabel_.textColor = [UIColor stampedLightGrayColor];
    locationLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:locationLabel_];
    [locationLabel_ release];
    
    bioLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(userImageView_.frame),
                                                          CGRectGetMaxY(userImageView_.frame) + 10,
                                                          300, 17)];
    bioLabel_.numberOfLines = 0;
    bioLabel_.lineBreakMode = UILineBreakModeWordWrap;
    bioLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    bioLabel_.textColor = [UIColor stampedGrayColor];
    bioLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:bioLabel_];
    [bioLabel_ release];
    
    followButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    [followButton_ setImage:[UIImage imageNamed:@"add_friends_follow_button"]
                   forState:UIControlStateNormal];
    followButton_.frame = CGRectMake(320 - 54 - 10, 20, 54, 30);
    [self.contentView addSubview:followButton_];
    
    unfollowButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    [unfollowButton_ setImage:[UIImage imageNamed:@"add_friends_unfollow_button"]
                     forState:UIControlStateNormal];
    unfollowButton_.frame = CGRectMake(320 - 66 - 10, 20, 66, 30);
    [self.contentView addSubview:unfollowButton_];
  }
  return self;
}

- (void)setUser:(User*)user {
  if (user_ != user) {
    [user_ release];
    user_ = [user retain];
  }

  if (user) {
    userImageView_.imageURL = [user profileImageURLForSize:ProfileImageSize46];
    stampImageView_.image = [user stampImageWithSize:StampImageSize46];
    usernameLabel_.text = user.screenName;
    fullNameLabel_.text = user.name;
    locationLabel_.text = user.location;
    bioLabel_.text = user.bio;
    // sizeToFit isn't working here for some reason.
    CGSize bioSize = [bioLabel_ sizeThatFits:CGSizeMake(300, MAXFLOAT)];
    bioLabel_.frame = CGRectMake(bioLabel_.frame.origin.x, bioLabel_.frame.origin.y, bioSize.width, bioSize.height);
  }
}

@end
