//
//  FindFriendsModalPreviewView.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "FindFriendsModalPreviewView.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "SocialManager.h"
#import "STImageView.h"
#import "UIColor+Stamped.h"

@interface FindFriendsModalPreviewView ()
- (void)commonInit;

@property (nonatomic, readonly) UIView* whiteView;
@property (nonatomic, readonly) STImageView* logoImageView;
@property (nonatomic, readonly) UIView* facebookMockView;
@property (nonatomic, readonly) UIImageView* emailImageView;
@end

@implementation FindFriendsModalPreviewView

@synthesize titleLabel = titleLabel_;
@synthesize whiteView = whiteView_;
@synthesize modalType = modalType_;
@synthesize numInvites = numInvites_;
@synthesize profileImageView = profileImageView_;
@synthesize headerLabel = headerLabel_;
@synthesize mainTextLabel = mainTextLabel_;
@synthesize logoImageView = logoImageView_;
@synthesize facebookMockView = facebookMockView_;
@synthesize emailImageView = emailImageView_;
@synthesize sampleTwitterUsername = sampleTwitterUsername_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self commonInit];

  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self commonInit];

  return self;
}

- (void)dealloc {
  titleLabel_ = nil;
  whiteView_ = nil;
  headerLabel_ = nil;
  profileImageView_ = nil;
  mainTextLabel_ = nil;
  logoImageView_ = nil;
  facebookMockView_ = nil;
  emailImageView_ = nil;
  self.sampleTwitterUsername = nil;
  [super dealloc];
}

- (void)commonInit {
  self.backgroundColor = [UIColor colorWithRed:0.23 green:0.23 blue:0.23 alpha:1.0];
  self.layer.cornerRadius = 4.0;
  self.layer.shadowOpacity = 0.5;
  self.layer.shadowOffset = CGSizeMake(0, 2);
  self.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:self.bounds cornerRadius:4.0].CGPath;

  titleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, CGRectGetWidth(self.bounds), 30)];
  titleLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  titleLabel_.textColor = [UIColor whiteColor];
  titleLabel_.shadowColor = [UIColor colorWithWhite:0 alpha:0.35];
  titleLabel_.shadowOffset = CGSizeMake(0, -1);
  titleLabel_.textAlignment = UITextAlignmentCenter;
  titleLabel_.backgroundColor = [UIColor clearColor];
  [self addSubview:titleLabel_];
  [titleLabel_ release];
  
  whiteView_ = [[UIView alloc] initWithFrame:CGRectZero];
  whiteView_.layer.cornerRadius = 3.0;
  whiteView_.backgroundColor = [UIColor whiteColor];
  [self addSubview:whiteView_];
  [whiteView_ release];
  
  // Email preview
  emailImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"invite_email_preview"]];
  [whiteView_ addSubview:emailImageView_];
  [emailImageView_ release];

  profileImageView_ = [[STImageView alloc] initWithFrame:CGRectMake(10, 14, 40, 40)];
  profileImageView_.layer.shadowOpacity = 0;
  profileImageView_.backgroundColor = [UIColor clearColor];
  [whiteView_ addSubview:profileImageView_];
  [profileImageView_ release];
  
  headerLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  headerLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  headerLabel_.backgroundColor = [UIColor clearColor];
  [whiteView_ addSubview:headerLabel_];
  [headerLabel_ release];
  
  mainTextLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  mainTextLabel_.numberOfLines = 0;
  mainTextLabel_.backgroundColor = [UIColor clearColor];
  mainTextLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
  mainTextLabel_.textColor = [UIColor stampedBlackColor];
  [whiteView_ addSubview:mainTextLabel_];
  [mainTextLabel_ release];
  
  facebookMockView_ = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 235, 75)];
  [whiteView_ addSubview:facebookMockView_];
  [facebookMockView_ release];

  // Facebook preview.
  logoImageView_ = [[STImageView alloc] initWithFrame:CGRectMake(0, 0, 50, 50)];
  logoImageView_.backgroundColor = [UIColor clearColor];
  logoImageView_.layer.shadowOpacity = 0;
  [facebookMockView_ addSubview:logoImageView_];
  [logoImageView_ release];

  UILabel* label = [[UILabel alloc] initWithFrame:CGRectZero];
  label.textColor = [UIColor colorWithRed:0.3 green:0.44 blue:0.77 alpha:1.0];
  label.backgroundColor = [UIColor clearColor];
  label.text = @"Stamped";
  label.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
  [label sizeToFit];
  label.frame = CGRectOffset(label.frame, 60, 0);
  [facebookMockView_ addSubview:label];
  [label release];

  label = [[UILabel alloc] initWithFrame:CGRectZero];
  label.textColor = [UIColor stampedGrayColor];
  label.backgroundColor = [UIColor clearColor];
  label.text = @"stamped.com";
  label.font = [UIFont fontWithName:@"Helvetica" size:10];
  [label sizeToFit];
  label.frame = CGRectOffset(label.frame, 60, 12);
  [facebookMockView_ addSubview:label];
  [label release];
  
  label = [[UILabel alloc] initWithFrame:CGRectZero];
  label.textColor = [UIColor stampedGrayColor];
  label.backgroundColor = [UIColor clearColor];
  label.text = @"Stamped is a new way to recommend only what you like best -- restaurants, books, movies, music and more.";
  label.font = [UIFont fontWithName:@"Helvetica" size:10];
  label.numberOfLines = 0;
  CGSize size = [label sizeThatFits:CGSizeMake(180, CGFLOAT_MAX)];
  label.frame = CGRectMake(60, 29, size.width, size.height);
  [facebookMockView_ addSubview:label];
  [label release];
  
  whiteView_.clipsToBounds = YES;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:self.bounds cornerRadius:4.0].CGPath;
}

- (void)setBounds:(CGRect)bounds {
  [super setBounds:bounds];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:self.bounds cornerRadius:4.0].CGPath;
}

- (void)layoutSubviews {
  [super layoutSubviews];
  headerLabel_.hidden = (modalType_ == FindFriendsModalTypeEmail);
  facebookMockView_.hidden = (modalType_ != FindFriendsModalTypeFacebook);
  emailImageView_.hidden = (modalType_ != FindFriendsModalTypeEmail);
  
  switch (modalType_) {
    case FindFriendsModalTypeEmail: {
      titleLabel_.text = @"Sample Email Invitation";
      User* currentUser = [AccountManager sharedManager].currentUser;
      mainTextLabel_.text = [NSString stringWithFormat:@"%@ (@%@) is inviting you to Stamped, a new way to recommend only what you like best.", currentUser.name, currentUser.screenName];
      mainTextLabel_.textAlignment = UITextAlignmentCenter;
      mainTextLabel_.font = [UIFont fontWithName:@"Helvetica" size:8];
      break;
    }
    case FindFriendsModalTypeTwitter:
      titleLabel_.text = @"Sample Invitation for Twitter";
      headerLabel_.text = [@"@" stringByAppendingString:[SocialManager sharedManager].twitterUsername];
      profileImageView_.imageURL = [SocialManager sharedManager].twitterProfileImageURL;
      if (!sampleTwitterUsername_)
        self.sampleTwitterUsername = @"@andybons";

      mainTextLabel_.text = [NSString stringWithFormat:@"%@ Hey, I'm using @stampedapp to share the restaurants, movies, books and music I like best. Join me at stamped.com.", sampleTwitterUsername_];
      mainTextLabel_.textAlignment = UITextAlignmentLeft;
      mainTextLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
      headerLabel_.textColor = [UIColor stampedBlackColor];
      break;
    case FindFriendsModalTypeFacebook:
      titleLabel_.text = @"Sample Invitation for Facebook";
      mainTextLabel_.textAlignment = UITextAlignmentLeft;
      mainTextLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
      headerLabel_.text = [SocialManager sharedManager].facebookName;
      headerLabel_.textColor = [UIColor colorWithRed:0.3 green:0.44 blue:0.77 alpha:1.0];
      profileImageView_.imageURL = [SocialManager sharedManager].facebookProfileImageURL;
      logoImageView_.imageURL = [SocialManager sharedManager].stampedLogoImageURL;
      mainTextLabel_.text = @"Hey, I think you have great taste, so join me on Stamped and share the things you like best.";
      break;
    default:
      break;
  }
  [headerLabel_ sizeToFit];
  headerLabel_.frame = CGRectMake(60, 12, CGRectGetWidth(headerLabel_.frame), CGRectGetHeight(headerLabel_.frame));

  if (modalType_ != FindFriendsModalTypeEmail) {
    CGSize size = [mainTextLabel_ sizeThatFits:CGSizeMake(235, CGFLOAT_MAX)];
    mainTextLabel_.frame = CGRectMake(CGRectGetMinX(headerLabel_.frame), CGRectGetMaxY(headerLabel_.frame) + 4, size.width, size.height);
  } else {
    CGSize size = [mainTextLabel_ sizeThatFits:CGSizeMake(220, CGFLOAT_MAX)];
    mainTextLabel_.frame = CGRectMake(45, 100, size.width, size.height);
  }
  if (modalType_ == FindFriendsModalTypeFacebook) {
    facebookMockView_.frame = CGRectMake(CGRectGetMinX(mainTextLabel_.frame),
                                         CGRectGetMaxY(mainTextLabel_.frame) + 8,
                                         CGRectGetWidth(facebookMockView_.frame),
                                         CGRectGetHeight(facebookMockView_.frame));
    self.bounds = CGRectMake(0, 0, CGRectGetWidth(self.bounds), CGRectGetMaxY(facebookMockView_.frame) + 46);
  } else if (modalType_ == FindFriendsModalTypeTwitter) {
    self.bounds = CGRectMake(0, 0, CGRectGetWidth(self.bounds), CGRectGetMaxY(mainTextLabel_.frame) + 48);
  } else if (modalType_ == FindFriendsModalTypeEmail) {
    self.bounds = CGRectMake(0, 0, CGRectGetWidth(self.bounds), 270);
  }
  whiteView_.frame = CGRectMake(2, 30, CGRectGetWidth(self.bounds) - 4, CGRectGetHeight(self.bounds) - 32);
}

- (CGSize)sizeThatFits:(CGSize)size {
  return [super sizeThatFits:size];
}


@end
