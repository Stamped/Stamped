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

    NSString* imageName = whiteAppearance ? @"nav_globe_button_ios5" : @"nav_globe_button_ios4";
    UIImage* globeImage = [UIImage imageNamed:imageName];
    self.mapButton = [UIButton buttonWithType:UIButtonTypeCustom];
    [mapButton_ setImage:globeImage forState:UIControlStateNormal];
    [mapButton_ addTarget:self
                     action:@selector(showListButton:)
           forControlEvents:UIControlEventTouchUpInside];
    mapButton_.adjustsImageWhenHighlighted = NO;
    mapButton_.frame = CGRectMake(0, 0, globeImage.size.width, globeImage.size.height);
    self.bounds = mapButton_.bounds;
    [self addSubview:mapButton_];
    
    imageName = whiteAppearance ? @"nav_list_button_ios5" : @"nav_list_button_ios4";
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
  UIView* black = [[UIView alloc] initWithFrame:CGRectInset(self.frame, 0, 1)];
  black.layer.cornerRadius = 5;
  black.backgroundColor = [UIColor blackColor];
  [self.superview insertSubview:black belowSubview:self];
  [black release];
  [UIView animateWithDuration:1 animations:^{
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self cache:YES];
    [sender removeFromSuperview];
    [self addSubview:listButton_];
  } completion:^(BOOL finished) {
    [black removeFromSuperview];
  }];
  [self sendActionsForControlEvents:UIControlEventTouchUpInside];
}

- (void)showMapButton:(id)sender {
  UIView* black = [[UIView alloc] initWithFrame:CGRectInset(self.frame, 0, 1)];
  black.layer.cornerRadius = 5;
  black.backgroundColor = [UIColor blackColor];
  [self.superview insertSubview:black belowSubview:self];
  [black release];
  [UIView animateWithDuration:1 animations:^ {
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromLeft forView:self cache:YES];
    [sender removeFromSuperview];
    [self addSubview:mapButton_];
  } completion:^(BOOL finished) {
    [black removeFromSuperview];
  }];
  [self sendActionsForControlEvents:UIControlEventTouchUpInside];
}

@end
