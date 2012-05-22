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
    
    UIImage *image = [UIImage imageNamed:@"search_gutter_bg.png"];
    self.background = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
    
    self.font = [UIFont fontWithName:@"Helvetica" size:14];
    self.autocorrectionType = UITextAutocorrectionTypeNo;
    self.returnKeyType = UIReturnKeySearch;
    self.enablesReturnKeyAutomatically = YES;
    self.keyboardAppearance = UIKeyboardAppearanceAlert;
    self.borderStyle = UITextBorderStyleNone;
    self.contentVerticalAlignment = UIControlContentVerticalAlignmentCenter;
    self.contentHorizontalAlignment = UIControlContentHorizontalAlignmentLeft;
    self.clearButtonMode = UITextFieldViewModeAlways;
    self.leftViewMode = UITextFieldViewModeAlways;
    UIView* leftView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 30, CGRectGetHeight(self.frame))];
    UIImageView* searchIcon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"search_icon"]];
    searchIcon.frame = CGRectOffset(searchIcon.frame, 10, 7);
    searchIcon.contentMode = UIViewContentModeCenter;
    [leftView addSubview:searchIcon];
    [searchIcon release];
    self.leftView = leftView;
    [leftView release];

}

- (CGRect)placeholderRectForBounds:(CGRect)bounds {
  // TODO(andybons): This will overflow if the placeholder is long enough.
  return CGRectOffset(bounds, 32, 0);
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

- (id)init {
  return [self initWithFrame:CGRectMake(0, 0, 320, 30)];
}

@end
