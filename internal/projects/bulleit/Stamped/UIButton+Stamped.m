//
//  UIButton+Stamped.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UIButton+Stamped.h"

@interface UIButton (StampedInternal)
+ (UIButton*)stampedButtonWithBackgroundImage:(UIImage*)bg highlightedBackgroundImage:(UIImage*)highlightedBg disabledBackgroundImage:(UIImage*)disabledBg;
@end

@implementation UIButton (Stamped)

+ (UIButton*)stampedFollowButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_green"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_green_hilited"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        disabledBackgroundImage:nil];

  [button setTitle:@"Follow" forState:UIControlStateNormal];
  [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:0 alpha:0.2] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, -1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  
  return button;
}

+ (UIButton*)stampedFollowingButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_white_hilited"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_white_pressed"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        disabledBackgroundImage:nil];

  [button setTitle:@"Following" forState:UIControlStateNormal];
  [button setTitleColor:[UIColor colorWithRed:0.33 green:0.6 blue:0.27 alpha:1.0] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:1 alpha:0.4] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, 1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];

  return button;
}

+ (UIButton*)stampedButtonWithBackgroundImage:(UIImage*)bg
                   highlightedBackgroundImage:(UIImage*)highlightedBg
                      disabledBackgroundImage:(UIImage*)disabledBg {
  UIButton* button = [UIButton buttonWithType:UIButtonTypeCustom];
  if ([bg respondsToSelector:@selector(resizableImageWithCapInsets:)]) {
    // iOS 5
    UIEdgeInsets insets = UIEdgeInsetsMake(4, 4, 4, 4);
    bg = [bg resizableImageWithCapInsets:insets];
    highlightedBg = [highlightedBg resizableImageWithCapInsets:insets];
    disabledBg = [disabledBg resizableImageWithCapInsets:insets];
  } else {
    // iOS 4
    bg = [bg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
    highlightedBg = [highlightedBg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
    disabledBg = [highlightedBg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
  }
  
  [button setBackgroundImage:bg forState:UIControlStateNormal];
  [button setBackgroundImage:highlightedBg forState:UIControlStateHighlighted];
  [button setBackgroundImage:disabledBg forState:UIControlStateDisabled];

  return button;
}

@end
