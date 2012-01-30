//
//  STSelectCountryTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSelectCountryTableViewCell.h"

#import "UIColor+Stamped.h"
#import "Util.h"

@interface STSelectCountryTableViewCell ()

@property (nonatomic, readonly) UIImageView* checkmarkImageView;

@end

@implementation STSelectCountryTableViewCell

@synthesize countryLabel = countryLabel_;
@synthesize checked = checked_;
@synthesize checkmarkImageView = checkmarkImageView_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    countryLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    countryLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    countryLabel_.textColor = [UIColor stampedBlackColor];
    countryLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:countryLabel_];
    [countryLabel_ release];
    
    UIImage* checkImage = [UIImage imageNamed:@"eCreate_country_check"];
    UIImage* highlightedImage = [Util whiteMaskedImageUsingImage:checkImage];
    checkmarkImageView_ = [[UIImageView alloc] initWithImage:checkImage highlightedImage:highlightedImage];
    checkmarkImageView_.hidden = YES;
    [self.contentView addSubview:checkmarkImageView_];
    [checkmarkImageView_ release];
  }
  return self;
}

- (void)dealloc {
  countryLabel_ = nil;
  checkmarkImageView_ = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  checkmarkImageView_.center = self.contentView.center;
  checkmarkImageView_.frame = CGRectMake(14, CGRectGetMinY(checkmarkImageView_.frame),
                                         CGRectGetWidth(checkmarkImageView_.frame),
                                         CGRectGetHeight(checkmarkImageView_.frame));
  if (checked_) {
    countryLabel_.textColor = [UIColor colorWithRed:0.22 green:0.48 blue:0.85 alpha:1.0];
  } else {
    countryLabel_.textColor = [UIColor blackColor];
  }
  checkmarkImageView_.hidden = !checked_;
  countryLabel_.frame = CGRectOffset(CGRectInset(self.contentView.bounds, 37.0 / 2.0, 0), 37.0 / 2.0, 0);
}

- (void)prepareForReuse {
  countryLabel_.textColor = [UIColor blackColor];
  countryLabel_.text = nil;
  checkmarkImageView_.hidden = YES;
  [super prepareForReuse];
}

@end
