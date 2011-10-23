//
//  STCreditTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditTextField.h"

#import <QuartzCore/QuartzCore.h>

@interface STCreditTextField ()
- (void)commonInit;
@end

@implementation STCreditTextField

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self commonInit];

  return self;
}

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self commonInit];

  return self;
}

- (void)commonInit {
  //self.backgroundColor = [UIColor grayColor];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
  self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
  self.layer.shadowOffset = CGSizeMake(0, 1);
  self.layer.shadowOpacity = 1.0;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (CGRect)textRectForBounds:(CGRect)bounds {
  return CGRectOffset(CGRectInset(bounds, 40, 0), 40, 0);
}

- (CGRect)editingRectForBounds:(CGRect)bounds {    
  return CGRectOffset(CGRectInset(bounds, 40, 0), 40, 0);
}

@end