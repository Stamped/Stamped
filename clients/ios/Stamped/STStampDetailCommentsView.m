//
//  STStampDetailCommentsView.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailCommentsView.h"

@interface STStampDetailCommentsView ()
- (void)_commonInit;
@end

@implementation STStampDetailCommentsView

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
  return CGSizeMake(310, MAX(51, size.height));
}

- (void)_commonInit {
  //self.backgroundColor = [UIColor colorWithRed:0 green:1 blue:0 alpha:0.5];
}

@end
