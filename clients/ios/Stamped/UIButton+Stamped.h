//
//  UIButton+Stamped.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface UIButton (Stamped)

+ (UIButton*)stampedFollowButton;
+ (UIButton*)stampedUnfollowButton;
+ (UIButton*)stampedBlueButton;
+ (UIButton*)stampedToolbarButton;
+ (UIButton*)stampedBlueToolbarButton;
+ (UIButton*)stampedWhiteButton;
+ (UIButton*)stampedPillButtonWithFrame:(CGRect)frame;

@end
