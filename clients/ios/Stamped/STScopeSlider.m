//
//  STInboxScopeSlider.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STScopeSlider.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "User.h"
#import "STTooltipView.h"
#import "STImageView.h"

@interface STScopeSlider ()
- (void)commonInit;
- (void)valueChanged:(id)sender;
- (void)dragEnded:(id)sender;
- (void)dragBegan:(id)sender;
- (void)updateImage;
- (void)updateTooltipPosition;
- (void)updateTooltipString;

@property (nonatomic, retain) STImageView* userImageView;
@property (nonatomic, readonly) STTooltipView* tooltipView;
@property (nonatomic, retain) NSMutableArray* trackButtons;
@end

@implementation STScopeSlider

@synthesize userImageView = userImageView_;
@synthesize trackButtons = trackButtons_;
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
  self.userImageView = nil;
  self.trackButtons = nil;
  [super dealloc];
}

- (void)commonInit {
    
    userImageView_ = [[STImageView alloc] initWithFrame:CGRectMake(0, 0, 26, 26)];
    userImageView_.imageURL = [[AccountManager sharedManager].currentUser profileImageURLForSize:ProfileImageSize31];
    userImageView_.layer.shadowOpacity = 0;
    userImageView_.backgroundColor = [UIColor clearColor];
    
    UIImageView* trackImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"scope_track"]];
    trackImageView.center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds) - 1);
    [self insertSubview:trackImageView atIndex:0];
    [trackImageView release];
    [self setMinimumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
    [self setMaximumTrackImage:[UIImage imageNamed:@"clear_image"] forState:UIControlStateNormal];
    [self addTarget:self action:@selector(valueChanged:) forControlEvents:UIControlEventValueChanged];
    [self addTarget:self action:@selector(dragEnded:) forControlEvents:(UIControlEventTouchUpInside | UIControlEventTouchUpOutside | UIControlEventTouchCancel)];
    [self addTarget:self action:@selector(dragBegan:) forControlEvents:UIControlEventTouchDown];
    tooltipView_ = [[STTooltipView alloc] initWithText:@"your friends"];
    tooltipView_.center = self.center;
    tooltipView_.frame = CGRectOffset(tooltipView_.frame, 0, -57);
    tooltipView_.alpha = 0;
    [self addSubview:tooltipView_];
    [tooltipView_ release];
    self.trackButtons = [NSMutableArray array];
    for (NSUInteger i = 0; i <= STStampedAPIScopeEveryone; ++i) {
        UIButton* b = [UIButton buttonWithType:UIButtonTypeCustom];
        b.tag = i;
        b.frame = CGRectMake((i / 4.0) * (CGRectGetWidth(self.bounds) + 30) - 2, -10, 40, 40);
        [b addTarget:self action:@selector(trackTapped:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:b];
        [trackButtons_ addObject:b];
    }
    [self setGranularity:STStampedAPIScopeFriends animated:NO];

}

- (void)flashTooltip {
  if ([tooltipView_.layer animationForKey:@"opacity"])
    return;
  
  [tooltipView_.layer removeAllAnimations];
  tooltipView_.alpha = 0;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction
                   animations:^{ tooltipView_.alpha = 1.0; }
                   completion:^(BOOL finished) {
                     [UIView animateWithDuration:0.3
                                           delay:2
                                         options:UIViewAnimationOptionAllowUserInteraction
                                      animations:^{ tooltipView_.alpha = 0; }
                                      completion:nil];
                   }];
  
}

- (void)updateTooltipPosition {
  CGFloat range = CGRectGetWidth(self.frame) - self.currentThumbImage.size.width;
  NSInteger xPos = ((self.value * range) + (self.currentThumbImage.size.width / 2.0));
  tooltipView_.center = CGPointMake(xPos, tooltipView_.center.y);
}

- (void)valueChanged:(id)sender {
  [self updateTooltipPosition];
  NSInteger quotient = (self.value / 0.333f) + 0.5f;
  granularity_ = quotient;
  [self updateImage];
  [self updateTooltipString];
}

- (void)updateTooltipString {
  NSString* string = nil;
  switch (granularity_) {
    case STStampedAPIScopeYou:
      string = NSLocalizedString(@"you", nil);
      break;
    case STStampedAPIScopeFriends:
      string = NSLocalizedString(@"you + friends", nil);
      break;
    case STStampedAPIScopeFriendsOfFriends:
      string = NSLocalizedString(@"friends of friends", nil);
      break;
    case STStampedAPIScopeEveryone:
      string = NSLocalizedString(@"popular", nil);
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
}

- (void)trackTapped:(id)sender {
  [self setGranularity:[sender tag] animated:YES];
}

- (void)setGranularity:(STStampedAPIScope)granularity animated:(BOOL)animated {
  if (granularity != granularity_) {
    granularity_ = granularity;
  }
  
  for (UIButton* b in trackButtons_)
    b.hidden = b.tag == granularity;
  
  if ([(id)delegate_ respondsToSelector:@selector(scopeSlider:didChangeGranularity:)])
    [delegate_ scopeSlider:self didChangeGranularity:granularity];
  
  [self updateImage];
  
  CGFloat value = granularity == 3 ? 1.0 : granularity * 0.333;
  [self setValue:value animated:animated];
  if (animated) {
    [UIView animateWithDuration:0.1 
                          delay:0
                        options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                     animations:^{
                       tooltipView_.alpha = 1.0;
                       [self updateTooltipString];
                       [self updateTooltipPosition];
                     } completion:^(BOOL finished) {
                       [UIView animateWithDuration:0.3
                                             delay:0.7
                                           options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                                        animations:^{ tooltipView_.alpha = 0.0; }
                                        completion:nil];
                     }];
  } else {
    [self updateTooltipString];
    [self updateTooltipPosition];
  }
}

- (void)updateImage {
  UIImage* background = [UIImage imageNamed:@"scope_drag_outer"];
  UIGraphicsBeginImageContextWithOptions(background.size, NO, 0.0);
  //[background drawInRect:CGRectMake(0, 0, background.size.width, background.size.height)];
  UIImage* inner = nil;
  switch (granularity_) {
    case STStampedAPIScopeYou:
      inner = [UIImage imageNamed:@"scope_drag_inner_you"];
      break;
    case STStampedAPIScopeFriends:
      inner = [UIImage imageNamed:@"scope_drag_inner_friends"];
      break;
    case STStampedAPIScopeFriendsOfFriends:
      inner = [UIImage imageNamed:@"scope_drag_inner_fof"];
      break;
    case STStampedAPIScopeEveryone:
      inner = [UIImage imageNamed:@"scope_drag_inner_all"];
      break;
    default:
      break;
  }
  CGFloat xPos = (background.size.width - inner.size.width) / 2;
  CGFloat yPos = ((background.size.height - inner.size.height) / 2) - 2;  // Account for shadow.
  if (granularity_ == STStampedAPIScopeYou &&
      ![[AccountManager sharedManager].currentUser.imageURL isEqualToString:@"http://static.stamped.com/users/default.jpg"] &&
      userImageView_.image) {
    CGPathRef maskPath = [UIBezierPath bezierPathWithOvalInRect:CGRectMake(xPos, yPos, 26, 26)].CGPath;
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextSaveGState(ctx);
    CGContextAddPath(ctx, maskPath);
    CGContextClip(ctx);
    [userImageView_.image drawInRect:CGRectMake(xPos, yPos, 26, 26)];
    CGContextRestoreGState(ctx);
  } else {
    [inner drawInRect:CGRectMake(xPos, yPos, inner.size.width, inner.size.height)];
  }
  UIImage* cover = [UIImage imageNamed:@"scope_drag_inner_cover"];
  [cover drawInRect:CGRectMake(xPos, yPos, cover.size.width, cover.size.height)];
  UIImage* final = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  [self setThumbImage:final forState:UIControlStateNormal];
}

@end
