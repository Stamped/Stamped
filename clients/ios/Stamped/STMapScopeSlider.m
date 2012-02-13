//
//  STMapScopeSlider.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapScopeSlider.h"

@interface STMapScopeSlider ()
- (void)commonInit;
- (void)valueChanged:(id)sender;
- (void)dragEnded:(id)sender;
- (void)updateImage;

@property (nonatomic, assign) STMapScopeSliderGranularity granularity;
@end

@implementation STMapScopeSlider

@synthesize granularity = granularity_;

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self commonInit];

  return self;
}

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self commonInit];
  
  return self;
}

- (void)commonInit {
  self.granularity = STMapScopeSliderGranularityFriends;
  UIImageView* trackImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"scope_track"]];
  trackImageView.center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds) - 1);
  [self insertSubview:trackImageView atIndex:0];
  [trackImageView release];
  [self setMinimumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
  [self setMaximumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
  [self addTarget:self action:@selector(valueChanged:) forControlEvents:UIControlEventValueChanged];
  [self addTarget:self action:@selector(dragEnded:) forControlEvents:(UIControlEventTouchUpInside | UIControlEventTouchUpOutside | UIControlEventTouchCancel)];
}

- (void)valueChanged:(id)sender {

}

- (void)dragEnded:(id)sender {
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  self.granularity = quotient;
  CGFloat value = (0.333 * quotient);
  if (quotient == 3)
    value = 1.0;
  [self setValue:value animated:YES];
}

- (void)setGranularity:(STMapScopeSliderGranularity)granularity {
  if (granularity != granularity_) {
    granularity_ = granularity;
    [self updateImage];
  }
}

- (void)updateImage {
  UIImage* background = [UIImage imageNamed:@"scope_drag_outer"];
  UIGraphicsBeginImageContextWithOptions(background.size, NO, 0.0);
  [background drawInRect:CGRectMake(0, 0, background.size.width, background.size.height)];
  UIImage* inner = nil;
  switch (granularity_) {
    case STMapScopeSliderGranularityYou:
      inner = [UIImage imageNamed:@"scope_drag_inner_you"];
      break;
    case STMapScopeSliderGranularityFriends:
      inner = [UIImage imageNamed:@"scope_drag_inner_friends"];
      break;
    case STMapScopeSliderGranularityFriendsOfFriends:
      inner = [UIImage imageNamed:@"scope_drag_inner_fof"];
      break;
    case STMapScopeSliderGranularityEveryone:
      inner = [UIImage imageNamed:@"scope_drag_inner_all"];
      break;
    default:
      break;
  }
  CGFloat xPos = (background.size.width - inner.size.width) / 2;
  CGFloat yPos = ((background.size.height - inner.size.height) / 2) - 2;  // Account for shadow.
  [inner drawInRect:CGRectMake(xPos, yPos, inner.size.width, inner.size.height)];
  UIImage* cover = [UIImage imageNamed:@"scope_drag_inner_cover"];
  [cover drawInRect:CGRectMake(xPos, yPos, cover.size.width, cover.size.height)];
  UIImage* final = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  [self setThumbImage:final forState:UIControlStateNormal];
}

@end
