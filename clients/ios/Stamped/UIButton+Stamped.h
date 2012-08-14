//
//  UIButton+Stamped.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 Legacy category
 
 I suggest deprecation and removal.
 
 2012-08-10
 -Landon
 */

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
