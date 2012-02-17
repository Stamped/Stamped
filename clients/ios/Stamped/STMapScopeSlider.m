//
//  STMapScopeSlider.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapScopeSlider.h"

#import "STTooltipView.h"

@interface STMapScopeSlider ()
- (void)commonInit;
- (void)valueChanged:(id)sender;
- (void)dragEnded:(id)sender;
- (void)dragBegan:(id)sender;
- (void)updateImage;
- (void)updateTooltipPosition;

@property (nonatomic, readonly) STTooltipView* tooltipView;
@end

@implementation STMapScopeSlider

@synthesize tooltipView = tooltipView_;
@synthesize granularity = granularity_;
@synthesize delegate = delegate_;

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

- (void)dealloc {
  delegate_ = nil;
  tooltipView_ = nil;
  [super dealloc];
}

- (void)commonInit {
  [self setGranularity:STMapScopeSliderGranularityFriends animated:NO];
  UIImageView* trackImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"scope_track"]];
  trackImageView.center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds) - 1);
  [self insertSubview:trackImageView atIndex:0];
  [trackImageView release];
  [self setMinimumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
  [self setMaximumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
  [self addTarget:self action:@selector(valueChanged:) forControlEvents:UIControlEventValueChanged];
  [self addTarget:self action:@selector(dragEnded:) forControlEvents:(UIControlEventTouchUpInside | UIControlEventTouchUpOutside | UIControlEventTouchCancel)];
  [self addTarget:self action:@selector(dragBegan:) forControlEvents:UIControlEventTouchDown];
  tooltipView_ = [[STTooltipView alloc] initWithText:@"friends of friends"];
  tooltipView_.center = self.center;
  tooltipView_.frame = CGRectOffset(tooltipView_.frame, 0, -57);
  tooltipView_.alpha = 0;
  [self addSubview:tooltipView_];
  [tooltipView_ release];
}

- (void)updateTooltipPosition {
  CGFloat range = CGRectGetWidth(self.frame) - self.currentThumbImage.size.width;
  NSInteger xPos = ((self.value * range) + (self.currentThumbImage.size.width / 2.0));
  tooltipView_.center = CGPointMake(xPos, tooltipView_.center.y);
}

- (void)valueChanged:(id)sender {
  [self updateTooltipPosition];
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  STMapScopeSliderGranularity granularity = quotient;
  NSString* string = nil;
  switch (granularity) {
    case STMapScopeSliderGranularityYou:
      string = @"you";
      break;
    case STMapScopeSliderGranularityFriends:
      string = @"friends";
      break;
    case STMapScopeSliderGranularityFriendsOfFriends:
      string = @"friends of friends";
      break;
    case STMapScopeSliderGranularityEveryone:
      string = @"popular";
      break;
    default:
      break;
  }
  if (string)
    [tooltipView_ setText:string animated:YES];
}

- (void)dragBegan:(id)sender {
  [self updateTooltipPosition];
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                   animations:^{ tooltipView_.alpha = 1.0; }
                   completion:nil];
}

- (void)dragEnded:(id)sender {
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  [self setGranularity:quotient animated:YES];
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                   animations:^{ tooltipView_.alpha = 0.0; }
                   completion:nil];
}

- (void)setGranularity:(STMapScopeSliderGranularity)granularity animated:(BOOL)animated {
  if (granularity != granularity_) {
    granularity_ = granularity;
    
    if ([(id)delegate_ respondsToSelector:@selector(mapScopeSlider:didChangeGranularity:)])
      [delegate_ mapScopeSlider:self didChangeGranularity:granularity];
    
    [self updateImage];
  }

  CGFloat value = granularity == 3 ? 1.0 : granularity * 0.333;
  [self setValue:value animated:animated];
  if (animated) {
    [UIView animateWithDuration:0.1 animations:^{
      [self updateTooltipPosition];
    }];
  } else {
    [self updateTooltipPosition];
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
