//
//  STUserCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserCell.h"
#import "Util.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"
#import "UIButton+Stamped.h"

static const CGFloat kUserImageSize = 41.0;

@interface STUserCell ()

@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) UILabel* fullNameLabel;
@property (nonatomic, readonly) UILabel* usernameLabel;

@end

@implementation STUserCell

@synthesize userImageView = userImageView_;
@synthesize stampImageView = stampImageView_;
@synthesize fullNameLabel = fullNameLabel_;
@synthesize usernameLabel = usernameLabel_;
@synthesize disclosureArrowImageView = disclosureArrowImageView_;
@synthesize indicator = indicator_;
@synthesize followButton = followButton_;
@synthesize unfollowButton = unfollowButton_;
@synthesize user = user_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(10, 5, kUserImageSize, kUserImageSize)];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];
    
    stampImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(CGRectGetMaxX(userImageView_.frame) + 18, 10, 14, 14)];
    [self.contentView addSubview:stampImageView_];
    [stampImageView_ release];
    
    fullNameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(stampImageView_.frame) + 7, 7, 181, 21)];
    fullNameLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    fullNameLabel_.highlightedTextColor = [UIColor whiteColor];
    fullNameLabel_.textColor = [UIColor stampedBlackColor];
    fullNameLabel_.backgroundColor = [UIColor clearColor];
    [self.contentView addSubview:fullNameLabel_];
    [fullNameLabel_ release];
    
    usernameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(fullNameLabel_.frame), 27, 181, 17)];
    usernameLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    usernameLabel_.backgroundColor = [UIColor clearColor];
    usernameLabel_.textColor = [UIColor stampedLightGrayColor];
    usernameLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:usernameLabel_];
    [usernameLabel_ release];
    
    UIImage* arrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    UIImage* highlightedArrowImage = [Util whiteMaskedImageUsingImage:arrowImage];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithImage:arrowImage
                                                  highlightedImage:highlightedArrowImage];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.frame = CGRectMake(292, 21, 11, 11);
    [self.contentView addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
    
    indicator_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    indicator_.hidesWhenStopped = YES;
    [indicator_ stopAnimating];
    [self.contentView addSubview:indicator_];
    [indicator_ release];
    
    followButton_ = [UIButton stampedFollowButton];
    [followButton_ sizeToFit];
    followButton_.frame = CGRectMake(320 - CGRectGetWidth(followButton_.frame) - 35, 10,
                                     CGRectGetWidth(followButton_.frame) + 30, 29);
    followButton_.hidden = YES;
    [self.contentView addSubview:followButton_];
    
    unfollowButton_ = [UIButton stampedUnfollowButton];
    [unfollowButton_ sizeToFit];
    unfollowButton_.frame = CGRectMake(320 - CGRectGetWidth(unfollowButton_.frame) - 20, 10,
                                       CGRectGetWidth(unfollowButton_.frame) + 15, 29);
    unfollowButton_.hidden = YES;
    [self.contentView addSubview:unfollowButton_];
  }
  return self;
}

- (void)dealloc {
  userImageView_ = nil;
  stampImageView_ = nil;
  fullNameLabel_ = nil;
  usernameLabel_ = nil;
  disclosureArrowImageView_ = nil;
  indicator_ = nil;
  followButton_ = nil;
  unfollowButton_ = nil;
  [super dealloc];
}

- (void)prepareForReuse {
  [super prepareForReuse];
  [userImageView_ resetImage];
  usernameLabel_.text = nil;
  fullNameLabel_.text = nil;
  stampImageView_.image = nil;
}

- (void)setUser:(id<STUser>)user {
  if (user_ != user) {
    [user_ release];
    user_ = [user retain];
  }
  
  if (user) {
    userImageView_.imageURL = [Util profileImageURLForUser:user withSize:STProfileImageSize48];
    stampImageView_.image = [Util stampImageForUser:user withSize:STStampImageSize14];
    usernameLabel_.text = user.screenName;
    fullNameLabel_.text = user.name;
  }
}

- (void)layoutSubviews {
  [super layoutSubviews];
  UIView* rightView = nil;
  NSArray* rightViews = [NSArray arrayWithObjects:disclosureArrowImageView_, followButton_, unfollowButton_, indicator_, nil];
  for (UIView* v in rightViews) {
    if (v.hidden == NO) {
      rightView = v;
      break;
    }
  }
  if (!rightView)
    return;
  
  CGRect frame = fullNameLabel_.frame;
  frame.size.width = CGRectGetMinX(rightView.frame) - CGRectGetMinX(frame) - 5;
  fullNameLabel_.frame = frame;
  frame = usernameLabel_.frame;
  frame.size.width = CGRectGetWidth(fullNameLabel_.frame);
  usernameLabel_.frame = frame;
}

@end
