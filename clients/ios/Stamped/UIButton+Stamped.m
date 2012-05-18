//
//  UIButton+Stamped.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UIButton+Stamped.h"
#import "UIColor+Stamped.h"
#import <QuartzCore/QuartzCore.h>

@interface UIButton (StampedInternal)
+ (UIButton*)stampedButtonWithBackgroundImage:(UIImage*)bg
                   highlightedBackgroundImage:(UIImage*)highlightedBg
                      selectedBackgroundImage:(UIImage*)selectedBg
                      disabledBackgroundImage:(UIImage*)disabledBg;
@end

@implementation UIButton (Stamped)

+ (UIButton*)stampedFollowButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_green"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_green_hilited"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:nil
                                        disabledBackgroundImage:nil];

  [button setTitle:@"Follow" forState:UIControlStateNormal];
  [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:0 alpha:0.2] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, -1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  
  return button;
}

+ (UIButton*)stampedUnfollowButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_white_hilited"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_white_pressed"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:nil
                                        disabledBackgroundImage:nil];

  [button setTitle:@"Unfollow" forState:UIControlStateNormal];
  [button setTitleColor:[UIColor colorWithRed:0.8 green:0.36 blue:0.32 alpha:1.0] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:1 alpha:0.4] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, 1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];

  return button;
}

+ (UIButton*)stampedBlueButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_blue"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_blue_hilited"];
  UIImage* disabledBg = [UIImage imageNamed:@"buttonBG_blue_disabled"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:nil
                                        disabledBackgroundImage:disabledBg];
  
  [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:0 alpha:0.2] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, -1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];

  return button;
}

+ (UIButton*)stampedToolbarButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_toolbar"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_white_hilited"];
  UIImage* selectedBg = [UIImage imageNamed:@"buttonBG_white_pressed"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:selectedBg
                                        disabledBackgroundImage:nil];
  
  [button setTitleColor:[UIColor stampedGrayColor] forState:UIControlStateNormal];
  [button setTitleColor:[UIColor stampedLightGrayColor] forState:UIControlStateDisabled];
  [button setTitleColor:[UIColor stampedDarkGrayColor] forState:UIControlStateHighlighted];
  [button setTitleColor:[UIColor colorWithRed:0.15 green:0.46 blue:0.89 alpha:1.0] forState:UIControlStateSelected];
  [button setTitleShadowColor:[UIColor colorWithWhite:1 alpha:0.5] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, 1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  
  return button;
}

+ (UIButton*)stampedBlueToolbarButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_toolbar"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_white_hilited"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:nil
                                        disabledBackgroundImage:nil];
  
  [button setTitleColor:[UIColor colorWithRed:0.15 green:0.46 blue:0.89 alpha:1.0] forState:UIControlStateNormal];
  [button setTitleColor:[UIColor stampedLightGrayColor] forState:UIControlStateDisabled];
  [button setTitleShadowColor:[UIColor colorWithWhite:1 alpha:0.5] forState:UIControlStateNormal];
  button.titleLabel.shadowOffset = CGSizeMake(0, 1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  
  return button;
}

+ (UIButton*)stampedWhiteButton {
  UIImage* bg = [UIImage imageNamed:@"buttonBG_white"];
  UIImage* highlightedBg = [UIImage imageNamed:@"buttonBG_white_hilited"];
  UIImage* selectedBg = [UIImage imageNamed:@"buttonBG_white_pressed"];
  UIImage* disabledBg = [UIImage imageNamed:@"buttonBG_blue_hilited"];
  UIButton* button = [UIButton stampedButtonWithBackgroundImage:bg
                                     highlightedBackgroundImage:highlightedBg
                                        selectedBackgroundImage:selectedBg
                                        disabledBackgroundImage:disabledBg];
  [button setTitleShadowColor:[UIColor colorWithWhite:1 alpha:0.4] forState:UIControlStateNormal];
  [button setTitleShadowColor:[UIColor colorWithWhite:0 alpha:0.2] forState:UIControlStateDisabled];
  [button setTitleColor:[UIColor whiteColor] forState:UIControlStateDisabled];
  button.titleLabel.shadowOffset = CGSizeMake(0, 1);
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  return button;
}

+ (UIButton*)stampedPillButtonWithFrame:(CGRect)frame {
  UIButton* button = [[[UIButton alloc] initWithFrame:frame] autorelease];
  button.layer.cornerRadius = MIN(frame.size.width / 2, frame.size.height / 2);
  //button.backgroundColor = [UIColor whiteColor];
  button.layer.borderColor = [UIColor colorWithWhite:229/255.0 alpha:1].CGColor;
  button.layer.borderWidth = 1;
  return button;
}

#pragma mark - Private methods.

+ (UIButton*)stampedButtonWithBackgroundImage:(UIImage*)bg
                   highlightedBackgroundImage:(UIImage*)highlightedBg
                      selectedBackgroundImage:(UIImage*)selectedBg
                      disabledBackgroundImage:(UIImage*)disabledBg {
  UIButton* button = [UIButton buttonWithType:UIButtonTypeCustom];
  button.adjustsImageWhenHighlighted = NO;
  button.adjustsImageWhenDisabled = NO;
  if ([bg respondsToSelector:@selector(resizableImageWithCapInsets:)]) {
    // iOS 5
    UIEdgeInsets insets = UIEdgeInsetsMake(4, 4, 4, 4);
    bg = [bg resizableImageWithCapInsets:insets];
    highlightedBg = [highlightedBg resizableImageWithCapInsets:insets];
    selectedBg = [selectedBg resizableImageWithCapInsets:insets];
    disabledBg = [disabledBg resizableImageWithCapInsets:insets];
  } else {
    // iOS 4
    bg = [bg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
    highlightedBg = [highlightedBg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
    selectedBg = [selectedBg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
    disabledBg = [disabledBg stretchableImageWithLeftCapWidth:4 topCapHeight:4];
  }
  
  [button setBackgroundImage:bg forState:UIControlStateNormal];
  [button setBackgroundImage:highlightedBg forState:UIControlStateHighlighted];
  [button setBackgroundImage:selectedBg forState:UIControlStateSelected];
  [button setBackgroundImage:disabledBg forState:UIControlStateDisabled];

  return button;
}

@end
