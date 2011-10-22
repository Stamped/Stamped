//
//  STCreditPill.m
//  CreditPillTest
//
//  Created by Andrew Bonventre on 10/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditPill.h"

#import <QuartzCore/QuartzCore.h>

@implementation STCreditPill

@synthesize textLabel = textLabel_;
@synthesize stampImageView = stampImageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.layer.cornerRadius = 12.5;
    self.layer.masksToBounds = YES;
    CAGradientLayer* gradientBorder = [[CAGradientLayer alloc] init];
    gradientBorder.frame = self.bounds;
    gradientBorder.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.9 alpha:1.0].CGColor,
                             (id)[UIColor colorWithWhite:0.8 alpha:1.0].CGColor, nil];
    gradientBorder.startPoint = CGPointMake(0, 0);
    gradientBorder.endPoint = CGPointMake(0, 1);
    [self.layer addSublayer:gradientBorder];
    [gradientBorder release];
  
    CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
    gradientLayer.colors =
        [NSArray arrayWithObjects:(id)[UIColor whiteColor].CGColor,
                                  (id)[UIColor colorWithWhite:0.9 alpha:1.0].CGColor, nil];
    gradientLayer.frame = CGRectInset(self.bounds, 1, 1);
    gradientLayer.cornerRadius = 11.5;
    gradientLayer.startPoint = CGPointMake(0, 0);
    gradientLayer.endPoint = CGPointMake(0, 1);
    [self.layer addSublayer:gradientLayer];
    [gradientLayer release];
    
    stampImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(6, 5, 15, 15)];
    stampImageView_.image = [UIImage imageNamed:@"baxter_stamp"];
    [self addSubview:stampImageView_];
    [stampImageView_ release];

    UILabel* atSymbolLabel = [[UILabel alloc] initWithFrame:CGRectMake(23, 2, 0, 0)];
    atSymbolLabel.text = @"@";
    [atSymbolLabel sizeToFit];
    atSymbolLabel.backgroundColor = [UIColor clearColor];
    atSymbolLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    atSymbolLabel.font = [UIFont fontWithName:@"Helvetica" size:11];
    atSymbolLabel.shadowColor = [UIColor whiteColor];
    atSymbolLabel.shadowOffset = CGSizeMake(0, 1);
    [self addSubview:atSymbolLabel];
    [atSymbolLabel release];

    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(34, 5, 0, 0)];
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.text = @"baxterjeff";
    textLabel_.textColor = [UIColor colorWithWhite:0.35 alpha:1.0];
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
  [super dealloc];
}

/*
// Only override drawRect: if you perform custom drawing.
// An empty implementation adversely affects performance during animation.
- (void)drawRect:(CGRect)rect
{
    // Drawing code
}
*/

@end
