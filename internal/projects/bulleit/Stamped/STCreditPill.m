//
//  STCreditPill.m
//  CreditPillTest
//
//  Created by Andrew Bonventre on 10/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditPill.h"

#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"

@interface STCreditPill ()
@property (nonatomic, readonly) UILabel* atSymbolLabel;
@property (nonatomic, readonly) CAGradientLayer* gradientBorder;
@property (nonatomic, readonly) CAGradientLayer* gradientBackground;
@end

@implementation STCreditPill

@synthesize textLabel = textLabel_;
@synthesize stampImageView = stampImageView_;
@synthesize atSymbolLabel = atSymbolLabel_;
@synthesize gradientBorder = gradientBorder_;
@synthesize gradientBackground = gradientBackground_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.layer.cornerRadius = 12.5;
    self.layer.masksToBounds = YES;
    gradientBorder_ = [[CAGradientLayer alloc] init];
    gradientBorder_.frame = self.bounds;
    gradientBorder_.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.9 alpha:1.0].CGColor,
                              (id)[UIColor colorWithWhite:0.8 alpha:1.0].CGColor, nil];
    gradientBorder_.startPoint = CGPointMake(0, 0);
    gradientBorder_.endPoint = CGPointMake(0, 1);
    [self.layer addSublayer:gradientBorder_];
    [gradientBorder_ release];
    
    gradientBackground_ = [[CAGradientLayer alloc] init];
    gradientBackground_.colors =
    [NSArray arrayWithObjects:(id)[UIColor whiteColor].CGColor,
        (id)[UIColor colorWithWhite:0.9 alpha:1.0].CGColor, nil];
    gradientBackground_.frame = CGRectInset(self.bounds, 1, 1);
    gradientBackground_.cornerRadius = 11.5;
    gradientBackground_.startPoint = CGPointMake(0, 0);
    gradientBackground_.endPoint = CGPointMake(0, 1);
    [self.layer addSublayer:gradientBackground_];
    [gradientBackground_ release];
    
    stampImageView_ = [[UIImageView alloc] initWithFrame:CGRectZero];
    [self addSubview:stampImageView_];
    [stampImageView_ release];
    [stampImageView_ sizeToFit];
    
    atSymbolLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    atSymbolLabel_.text = @"@";
    atSymbolLabel_.backgroundColor = [UIColor clearColor];
    atSymbolLabel_.textColor = [UIColor stampedGrayColor];
    atSymbolLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
    atSymbolLabel_.shadowColor = [UIColor whiteColor];
    atSymbolLabel_.shadowOffset = CGSizeMake(0, 1);
    [self addSubview:atSymbolLabel_];
    [atSymbolLabel_ release];
    
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor stampedDarkGrayColor];
    textLabel_.shadowColor = [UIColor whiteColor];
    textLabel_.shadowOffset = CGSizeMake(0, 1);
    textLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:11];
    [textLabel_ sizeToFit];
    [self addSubview:textLabel_];
    [textLabel_ release];
  }
  return self;
}

- (void)dealloc {
  textLabel_ = nil;
  stampImageView_ = nil;
  atSymbolLabel_ = nil;
  gradientBorder_ = nil;
  gradientBackground_ = nil;
  [super dealloc];
}

- (CGSize)sizeThatFits:(CGSize)size {
  CGFloat stampImageWidth = 19.0;
  if (!stampImageView_.image)
    stampImageWidth = 0.0;
  
  [textLabel_ sizeToFit];
  return CGSizeMake(stampImageWidth + CGRectGetWidth(textLabel_.frame) + 26, 25);
}

- (void)layoutSubviews {
  gradientBorder_.frame = self.bounds;
  gradientBackground_.frame = CGRectInset(self.bounds, 1, 1);
  
  BOOL hasStampImage = stampImageView_.image != nil;
  if (hasStampImage)
    stampImageView_.frame = CGRectMake(6, 5, 15, 15);
  
  CGFloat xPos = hasStampImage ? 25.0 : 6.0;
  atSymbolLabel_.frame = CGRectMake(xPos, 5, 0, 0);
  [atSymbolLabel_ sizeToFit];
  
  xPos = hasStampImage ? 36.0 : 17.0;
  textLabel_.frame = CGRectMake(xPos, 5, 0, 0);
  [textLabel_ sizeToFit];
}

@end