//
//  STCreditTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STCreditTextField.h"

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
  
}

- (CGRect)textRectForBounds:(CGRect)bounds {
  return CGRectOffset(CGRectInset(bounds, 40, 0), 40, 0);
}

- (CGRect)editingRectForBounds:(CGRect)bounds {    
  return CGRectOffset(CGRectInset(bounds, 40, 0), 40, 0);
}

@end