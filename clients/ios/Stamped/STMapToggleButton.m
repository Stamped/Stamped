//
//  STMapToggleButton.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapToggleButton.h"

#import <QuartzCore/QuartzCore.h>

@interface STMapToggleButton ()
- (void)showListButton:(id)sender;
- (void)showMapButton:(id)sender;
@end

@implementation STMapToggleButton

@synthesize mapButton = mapButton_;
@synthesize listButton = listButton_;

- (id)init {
  self = [super init];
  if (self) {
    BOOL whiteAppearance = NO;
    if ([UINavigationBar conformsToProtocol:@protocol(UIAppearance)])
      whiteAppearance = YES;

    UIImage* mapImage = [UIImage imageNamed:@"nav_map_button"];
    self.mapButton = [UIButton buttonWithType:UIButtonTypeCustom];
    [mapButton_ setImage:mapImage forState:UIControlStateNormal];
    [mapButton_ addTarget:self
                     action:@selector(showListButton:)
           forControlEvents:UIControlEventTouchUpInside];
    mapButton_.adjustsImageWhenHighlighted = NO;
    mapButton_.frame = CGRectMake(0, 0, mapImage.size.width, mapImage.size.height);
    self.bounds = mapButton_.bounds;
    [self addSubview:mapButton_];
    
    NSString* imageName = whiteAppearance ? @"nav_list_button_ios5" : @"nav_list_button_ios4";
    UIImage* listImage = [UIImage imageNamed:imageName];
    self.listButton = [UIButton buttonWithType:UIButtonTypeCustom];
    listButton_.adjustsImageWhenHighlighted = NO;
    [listButton_ setImage:listImage forState:UIControlStateNormal];
    [listButton_ addTarget:self
                    action:@selector(showMapButton:)
          forControlEvents:UIControlEventTouchUpInside];
    listButton_.frame = CGRectMake(0, 0, listImage.size.width, listImage.size.height);
    self.bounds = listButton_.bounds;
  }
  return self;
}

- (void)dealloc {
  self.mapButton = nil;
  self.listButton = nil;
  [super dealloc];
}

- (void)showListButton:(id)sender {
  UIImageView* background = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"map_flippy_button"]];
  background.frame = CGRectMake(self.frame.origin.x, self.frame.origin.y, CGRectGetWidth(background.frame), CGRectGetHeight(background.frame));
  [self.superview insertSubview:background belowSubview:self];
  [background release];
  [UIView animateWithDuration:1 animations:^{
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self cache:YES];
    [sender removeFromSuperview];
    [self addSubview:listButton_];
  } completion:^(BOOL finished) {
    [background removeFromSuperview];
  }];
  [self sendActionsForControlEvents:UIControlEventTouchUpInside];
}

- (void)showMapButton:(id)sender {
  UIImageView* background = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"map_flippy_button"]];
  background.frame = CGRectMake(self.frame.origin.x, self.frame.origin.y, CGRectGetWidth(background.frame), CGRectGetHeight(background.frame));
  [self.superview insertSubview:background belowSubview:self];
  [background release];
  [UIView animateWithDuration:1 animations:^ {
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromLeft forView:self cache:YES];
    [sender removeFromSuperview];
    [self addSubview:mapButton_];
  } completion:^(BOOL finished) {
    [background removeFromSuperview];
  }];
  [self sendActionsForControlEvents:UIControlEventTouchUpInside];
}

@end
