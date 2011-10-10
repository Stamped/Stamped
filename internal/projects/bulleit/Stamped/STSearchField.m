//
//  STSearchField.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STSearchField.h"

@interface STSearchField ()
- (void)initialize;
@end

@implementation STSearchField

- (void)initialize {
  self.background = [[UIImage imageNamed:@"search_field_background"] stretchableImageWithLeftCapWidth:35
                                                                                         topCapHeight:0];
  self.font = [UIFont fontWithName:@"Helvetica" size:14];
  self.autocorrectionType = UITextAutocorrectionTypeNo;
  self.returnKeyType = UIReturnKeySearch;
  self.enablesReturnKeyAutomatically = YES;
  self.keyboardAppearance = UIKeyboardAppearanceAlert;
  self.borderStyle = UITextBorderStyleNone;
  self.contentVerticalAlignment = UIControlContentVerticalAlignmentCenter;
  self.contentHorizontalAlignment = UIControlContentHorizontalAlignmentLeft;
  self.clearButtonMode = UITextFieldViewModeWhileEditing;
  self.leftViewMode = UITextFieldViewModeAlways;
  UIView* leftView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 32, CGRectGetHeight(self.frame))];
  UIImageView* searchIcon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_icon"]];
  searchIcon.frame = CGRectOffset(searchIcon.frame, 10, 8);
  searchIcon.contentMode = UIViewContentModeCenter;
  [leftView addSubview:searchIcon];
  [searchIcon release];
  self.leftView = leftView;
  [leftView release];
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self initialize];
  }
  return self;
}

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self initialize];
  }
  return self;
}

@end
