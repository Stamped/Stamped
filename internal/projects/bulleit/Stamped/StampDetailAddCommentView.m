//
//  StampDetailAddCommentView.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/18/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailAddCommentView.h"

#import <QuartzCore/QuartzCore.h>

#import "UserImageView.h"

@interface StampDetailAddCommentView ()
- (void)setup;
@end

@implementation StampDetailAddCommentView

@synthesize userImageView = userImageView_;
@synthesize commentTextField = commentTextField_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self setup];

  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self setup];

  return self;
}

- (void)setup {
  self.backgroundColor = [UIColor whiteColor];
  userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(10, 11, 31, 31)];
  [self addSubview:userImageView_];
  [userImageView_ release];
  commentTextField_ = [[UITextField alloc] initWithFrame:CGRectMake(52, 11, 250, 31)];
  commentTextField_.placeholder = @"Add a comment";
  commentTextField_.keyboardAppearance = UIKeyboardAppearanceAlert;
  commentTextField_.font = [UIFont fontWithName:@"Helvetica" size:14];
  commentTextField_.borderStyle = UITextBorderStyleRoundedRect;
  commentTextField_.contentVerticalAlignment = UIControlContentVerticalAlignmentCenter;
  [self addSubview:commentTextField_];
  [commentTextField_ release];
  self.layer.shadowOffset = CGSizeZero;
  self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.9 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, 0, CGRectGetWidth(self.bounds), 1));
  CGContextRestoreGState(ctx);
}

@end
