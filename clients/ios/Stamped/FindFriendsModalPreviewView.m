//
//  FindFriendsModalPreviewView.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "FindFriendsModalPreviewView.h"

#import <QuartzCore/QuartzCore.h>

#import "STImageView.h"
#import "UIColor+Stamped.h"

@interface FindFriendsModalPreviewView ()
- (void)commonInit;

@property (nonatomic, readonly) UIView* whiteView;
@end

@implementation FindFriendsModalPreviewView

@synthesize titleLabel = titleLabel_;
@synthesize whiteView = whiteView_;
@synthesize modalType = modalType_;
@synthesize numInvites = numInvites_;
@synthesize profileImageView = profileImageView_;
@synthesize headerLabel = headerLabel_;
@synthesize mainTextLabel = mainTextLabel_;

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
  titleLabel_.text = @"Invitation for Facebook";
  titleLabel_.textAlignment = UITextAlignmentCenter;
  titleLabel_.backgroundColor = [UIColor clearColor];
  [self addSubview:titleLabel_];
  [titleLabel_ release];
  
  whiteView_ = [[UIView alloc] initWithFrame:CGRectZero];
  whiteView_.layer.cornerRadius = 3.0;
  whiteView_.backgroundColor = [UIColor whiteColor];
  [self addSubview:whiteView_];
  [whiteView_ release];

  profileImageView_ = [[STImageView alloc] initWithFrame:CGRectZero];
  profileImageView_.layer.shadowOpacity = 0;
  [whiteView_ addSubview:profileImageView_];
  [profileImageView_ release];
  
  headerLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  headerLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:11];
  [whiteView_ addSubview:headerLabel_];
  [headerLabel_ release];
  
  mainTextLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  mainTextLabel_.numberOfLines = 0;
  mainTextLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
  mainTextLabel_.textColor = [UIColor stampedBlackColor];
  [whiteView_ addSubview:mainTextLabel_];
  [mainTextLabel_ release];
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
  headerLabel_.text = @"@edmuki";
  headerLabel_.hidden = (modalType_ == FindfriendsModalTypeEmail);
  switch (modalType_) {
    case FindfriendsModalTypeEmail:
    
      break;
    case FindFriendsModalTypeTwitter:
      headerLabel_.textColor = [UIColor stampedBlackColor];
      break;
    case FindFriendsModalTypeFacebook:
      headerLabel_.textColor = [UIColor colorWithRed:0.3 green:0.44 blue:0.77 alpha:1.0];
    default:
      break;
  }
  [headerLabel_ sizeToFit];
  headerLabel_.frame = CGRectMake(55, 15, CGRectGetWidth(headerLabel_.frame), CGRectGetHeight(headerLabel_.frame));
  
  mainTextLabel_.text = @"@andybons Hey, I'm using @stampedapp to share the restaurants, movies, books and music I like best. Join me at stamped.com.";
  CGSize size = [mainTextLabel_ sizeThatFits:CGSizeMake(235, CGFLOAT_MAX)];
  mainTextLabel_.frame = CGRectMake(CGRectGetMinX(headerLabel_.frame), CGRectGetMaxY(headerLabel_.frame) + 4, size.width, size.height);
  self.bounds = CGRectMake(0, 0, CGRectGetWidth(self.bounds), CGRectGetMaxY(mainTextLabel_.frame) + 48);
  whiteView_.frame = CGRectMake(2, 30, CGRectGetWidth(self.bounds) - 4, CGRectGetHeight(self.bounds) - 32);
}

- (CGSize)sizeThatFits:(CGSize)size {
  return [super sizeThatFits:size];
}


@end
