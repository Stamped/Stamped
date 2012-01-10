//
//  STAddCommentTextField.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STAddCommentTextField.h"

const CGFloat kLeftInset = 4.0;

@implementation STAddCommentTextField

- (CGRect)textRectForBounds:(CGRect)bounds {
  return CGRectOffset(CGRectInset(bounds, kLeftInset, 0), kLeftInset / 2, 0);
}

- (CGRect)editingRectForBounds:(CGRect)bounds {
  return [self textRectForBounds:bounds];
}

@end
