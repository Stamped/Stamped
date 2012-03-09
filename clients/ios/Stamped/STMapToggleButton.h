//
//  STMapToggleButton.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STMapToggleButton : UIControl

- (void)showListButton:(id)sender;
- (void)showMapButton:(id)sender;

@property (nonatomic, retain) UIButton* mapButton;
@property (nonatomic, retain) UIButton* listButton;

@end
