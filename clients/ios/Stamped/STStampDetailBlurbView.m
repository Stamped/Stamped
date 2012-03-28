//
//  STStampDetailBlurbView.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailBlurbView.h"

#import "TTTAttributedLabel.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

@interface STStampDetailBlurbView ()
@property (nonatomic, readonly) UILabel* stampedLabel;

- (void)_commonInit;
@end

@implementation STStampDetailBlurbView

@synthesize userImageView = _userImageView;
@synthesize nameLabel = _nameLabel;
@synthesize stampedLabel = _stampedLabel;
@synthesize timestampLabel = _timestampLabel;
@synthesize blurbLabel = _blurbLabel;

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

- (CGSize)sizeThatFits:(CGSize)size {
  return CGSizeMake(size.width, MAX(81, CGRectGetMaxY(_blurbLabel.frame)));
}

- (void)layoutSubviews {
  [super layoutSubviews];
  [_nameLabel sizeToFit];
  _nameLabel.frame = CGRectMake(CGRectGetMaxX(_userImageView.frame) + 10,
                                CGRectGetMinY(_userImageView.frame) + 3, 
                                CGRectGetWidth(_nameLabel.frame), CGRectGetHeight(_nameLabel.frame));
  CGRect frame = _stampedLabel.frame;
  frame.origin.x = CGRectGetMaxX(_nameLabel.frame) + 3;
  frame.origin.y = CGRectGetMinY(_nameLabel.frame);
  _stampedLabel.frame = frame;

  [_timestampLabel sizeToFit];
  _timestampLabel.frame = CGRectMake(310 - CGRectGetWidth(_timestampLabel.frame) - 10,
                                     19,
                                     CGRectGetWidth(_timestampLabel.frame),
                                     CGRectGetHeight(_timestampLabel.frame));
  
  CGSize stringSize = [_blurbLabel sizeThatFits:CGSizeMake(210, MAXFLOAT)];
  _blurbLabel.frame = CGRectMake(CGRectGetMaxX(_userImageView.frame) + 10,
                                 CGRectGetMaxY(_nameLabel.frame) + 1,
                                 stringSize.width, stringSize.height);
}

- (void)_commonInit {  
  _userImageView = [[UserImageView alloc] initWithFrame:CGRectMake(9, 12, 59, 59)];
  [self addSubview:_userImageView];
  [_userImageView release];
  
  _nameLabel = [[TTTAttributedLabel alloc] initWithFrame:CGRectZero];
  _nameLabel.textColor = [UIColor stampedGrayColor];
  _nameLabel.font = [UIFont boldSystemFontOfSize:14];
  [self addSubview:_nameLabel];
  [_nameLabel release];
  
  _stampedLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  _stampedLabel.text = NSLocalizedString(@"stamped", nil);
  _stampedLabel.textColor = [UIColor stampedGrayColor];
  _stampedLabel.font = [UIFont systemFontOfSize:14];
  [_stampedLabel sizeToFit];
  [self addSubview:_stampedLabel];
  [_stampedLabel release];
  
  _timestampLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  _timestampLabel.textColor = [UIColor stampedLightGrayColor];
  _timestampLabel.font = [UIFont boldSystemFontOfSize:10];
  [self addSubview:_timestampLabel];
  [_timestampLabel release];
  
  _blurbLabel = [[TTTAttributedLabel alloc] initWithFrame:CGRectZero];
  _blurbLabel.userInteractionEnabled = YES;
  _blurbLabel.textColor = [UIColor stampedBlackColor];
  _blurbLabel.font = [UIFont systemFontOfSize:14];
  _blurbLabel.lineBreakMode = UILineBreakModeWordWrap;
  _blurbLabel.numberOfLines = 0;
  [self addSubview:_blurbLabel];
  [_blurbLabel release];

  UIImageView* keyline = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"blurbView_keyline"]];
  keyline.frame = CGRectOffset(keyline.frame, 0, CGRectGetMaxY(self.bounds) - 1);
  [self addSubview:keyline];
  [keyline release];
  //self.backgroundColor = [UIColor grayColor];
}

@end
