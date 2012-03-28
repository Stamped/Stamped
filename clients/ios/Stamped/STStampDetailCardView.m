//
//  STStampDetailCardView.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailCardView.h"

#import <QuartzCore/QuartzCore.h>

#import "Stamp.h"
#import "STStampDetailBlurbView.h"
#import "STStampDetailCommentsView.h"
#import "TTTAttributedLabel.h"
#import "User.h"
#import "UserImageView.h"
#import "Util.h"

@interface STStampDetailCardView ()
@property (nonatomic, readonly) CAGradientLayer* backgroundGradient;
@property (nonatomic, readonly) STStampDetailBlurbView* blurbView;
@property (nonatomic, readonly) STStampDetailCommentsView* commentsView;

- (void)_commonInit;
@end

@implementation STStampDetailCardView

@synthesize stamp = _stamp;
@synthesize blurbView = _blurbView;
@synthesize backgroundGradient = _backgroundGradient;
@synthesize commentsView = _commentsView;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (void)dealloc {
  [_stamp release];
  [super dealloc];
}

- (CGSize)sizeThatFits:(CGSize)size {
  return CGSizeMake(310, MAX(size.height, 137));
}

- (void)layoutSubviews {
  [super layoutSubviews];

  _backgroundGradient.frame = CGRectInset(self.bounds, 0, 1);
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:_stamp.user.primaryColor toRed:&r1 green:&g1 blue:&b1];
  if (_stamp.user.secondaryColor) {
    [Util splitHexString:_stamp.user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  _backgroundGradient.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.9].CGColor,
                                (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.9].CGColor,
                                nil];
  _blurbView.userImageView.imageURL = [_stamp.user profileImageURLForSize:ProfileImageSize55];
  _blurbView.nameLabel.text = _stamp.user.screenName;
  _blurbView.timestampLabel.text = [Util shortUserReadableTimeSinceDate:_stamp.created];
  _blurbView.blurbLabel.text = _stamp.blurb;
  [_blurbView layoutIfNeeded];
  [_blurbView sizeToFit];
  [_commentsView sizeToFit];
  _commentsView.frame = CGRectMake(0, CGRectGetMaxY(_blurbView.frame),
                                   CGRectGetWidth(_commentsView.frame),
                                   CGRectGetHeight(_commentsView.frame));
  
}

#pragma mark - Private methods.

- (void)_commonInit {
  self.backgroundColor = [UIColor whiteColor];
  self.layer.shadowColor = [UIColor blackColor].CGColor;
  self.layer.shadowOpacity = 0.2;
  self.layer.shadowOffset = CGSizeMake(0, 4);
  self.layer.shadowRadius = 4;
  _backgroundGradient = [CAGradientLayer layer];
  _backgroundGradient.startPoint = CGPointMake(0, 0);
  _backgroundGradient.endPoint = CGPointMake(1, 1);
  [self.layer addSublayer:_backgroundGradient];
  UIImageView* topRibbonView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_detail_ripple_top"]];
  topRibbonView.frame = CGRectOffset(topRibbonView.frame, 0, 1);
  topRibbonView.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
  [self addSubview:topRibbonView];
  [topRibbonView release];
  UIImageView* botRibbonView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamp_detail_ripple_bottom"]];
  botRibbonView.frame = CGRectOffset(botRibbonView.frame, 0, CGRectGetHeight(self.bounds) - CGRectGetHeight(botRibbonView.frame) - 1);
  botRibbonView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;
  [self addSubview:botRibbonView];
  [botRibbonView release];
  UIView* whiteMask = [[UIView alloc] initWithFrame:CGRectMake(0, CGRectGetMaxY(topRibbonView.frame),
                                                               310, CGRectGetMinY(botRibbonView.frame) - CGRectGetMaxY(topRibbonView.frame))];
  whiteMask.autoresizingMask = UIViewAutoresizingFlexibleHeight;
  whiteMask.backgroundColor = [UIColor whiteColor];
  [self addSubview:whiteMask];
  [whiteMask release];
  
  _commentsView = [[STStampDetailCommentsView alloc] initWithFrame:CGRectZero];
  [self addSubview:_commentsView];
  [_commentsView release];

  // Blurb view must be on top of the comments view because it has a shadow that extends
  // beyond its bounds.
  _blurbView = [[STStampDetailBlurbView alloc] initWithFrame:CGRectMake(0, 0, 310, 81)];
  _blurbView.autoresizingMask = UIViewAutoresizingFlexibleHeight;
  [self addSubview:_blurbView];
  [_blurbView release];
}

@end
