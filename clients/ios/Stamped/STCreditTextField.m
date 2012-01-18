//
//  STCreditTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditTextField.h"

#import <QuartzCore/QuartzCore.h>

#import "STCreditPill.h"
#import "UIColor+Stamped.h"
  
@interface STCreditTextField ()
- (void)commonInit;

@property (nonatomic, readonly) UITextField* textField;
@end

@implementation STCreditTextField

@synthesize textField = textField_;
@synthesize titleLabel = titleLabel_;

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

- (void)dealloc {
  titleLabel_ = nil;
  textField_.delegate = nil;
  textField_ = nil;
  [super dealloc];
}

- (void)commonInit {
  UIImageView* creditIcon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_icon"]];
  creditIcon.frame = CGRectOffset(creditIcon.frame, 12, 20);
  [self addSubview:creditIcon];
  [creditIcon release];
  
  titleLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  titleLabel_.textColor = [UIColor stampedGrayColor];
  titleLabel_.text = @"Who deserves credit?";
  titleLabel_.font = [UIFont fontWithName:@"Helvetica" size:11];
  [titleLabel_ sizeToFit];
  titleLabel_.frame = CGRectOffset(titleLabel_.frame,
                                   CGRectGetMaxX(creditIcon.frame) + 3,
                                   CGRectGetMinY(creditIcon.frame) - 2);
  [self addSubview:titleLabel_];
  [titleLabel_ release];
  self.backgroundColor = [UIColor whiteColor];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
  self.layer.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2].CGColor;
  self.layer.shadowOffset = CGSizeMake(0, 1);
  
  textField_ = [[UITextField alloc] initWithFrame:CGRectZero];
  textField_.autocorrectionType = UITextAutocorrectionTypeNo;
  textField_.keyboardAppearance = UIKeyboardAppearanceAlert;
  textField_.autocapitalizationType = UITextAutocapitalizationTypeNone;
  textField_.returnKeyType = UIReturnKeyDone;
  textField_.font = [UIFont fontWithName:@"Helvetica" size:14];
  [self addSubview:textField_];
  [textField_ release];
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setDelegate:(id<UITextFieldDelegate>)delegate {
  textField_.delegate = delegate;
}

- (id<UITextFieldDelegate>)delegate {
  return textField_.delegate;
}

- (void)setText:(NSString*)text {
  textField_.text = text;
}

- (NSString*)text {
  return textField_.text;
}

- (BOOL)becomeFirstResponder {
  return [textField_ becomeFirstResponder];
}

- (BOOL)resignFirstResponder {
  return [textField_ resignFirstResponder];
}

- (void)layoutSubviews {
  CGFloat yPos = 12.0;
  [titleLabel_ sizeToFit];
  CGFloat xPos = CGRectGetMaxX(titleLabel_.frame) + 4;
  for (UIView* view in self.subviews) {
    if (![view isMemberOfClass:[STCreditPill class]])
      continue;

    STCreditPill* pill = (STCreditPill*)view;
    CGRect pillFrame = pill.frame;
    CGFloat widthNeeded = CGRectGetWidth(pillFrame) + 5;
    if (xPos + widthNeeded > CGRectGetWidth(self.bounds)) {
      yPos += 30.0;
      xPos = 10.0;
    }
    pillFrame.origin = CGPointMake(xPos, yPos);
    pill.frame = pillFrame;
    xPos += widthNeeded;
  }
  [textField_ sizeToFit];
  if (xPos + CGRectGetWidth(textField_.bounds) > CGRectGetWidth(self.bounds)) {
    xPos = 10.0;
    yPos += 30.0;
  }
  textField_.frame = CGRectMake(xPos, yPos + 2, 
                                CGRectGetWidth(textField_.bounds) + 4,
                                CGRectGetHeight(textField_.bounds));
  [self sizeToFit];
}

- (CGSize)sizeThatFits:(CGSize)size {
  return CGSizeMake(size.width, MAX(48, textField_.frame.origin.y + 33));
}

#pragma mark - UIResponder methods.

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  [super touchesEnded:touches withEvent:event];
  [self.textField becomeFirstResponder];
}

@end