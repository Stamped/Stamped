//
//  STMapIndicatorView.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapIndicatorView.h"

#import <QuartzCore/QuartzCore.h>

@interface STMapIndicatorView ()
@property (nonatomic, readonly) UIImageView* backgroundImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* indicatorView;
@property (nonatomic, readonly) UILabel* noResultsLabel;
@end

@implementation STMapIndicatorView

@synthesize mode = mode_;
@synthesize backgroundImageView = backgroundImageView_;
@synthesize indicatorView = indicatorView_;
@synthesize noResultsLabel = noResultsLabel_;

- (id)init {
  self = [super initWithFrame:CGRectZero];
  if (self) {
    UIImage* backgroundImage = [[UIImage imageNamed:@"map_loading_overlay"] stretchableImageWithLeftCapWidth:10 topCapHeight:10];
    backgroundImageView_ = [[UIImageView alloc] initWithImage:backgroundImage];
    backgroundImageView_.contentMode = UIViewContentModeScaleToFill;
    [self addSubview:backgroundImageView_];
    [backgroundImageView_ release];
    self.frame = backgroundImageView_.bounds;
    indicatorView_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
    indicatorView_.center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds) - 2);
    indicatorView_.hidesWhenStopped = YES;
    [indicatorView_ stopAnimating];
    [self addSubview:indicatorView_];
    [indicatorView_ release];
    
    noResultsLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    noResultsLabel_.alpha = 0;
    noResultsLabel_.textAlignment = UITextAlignmentCenter;
    noResultsLabel_.textColor = [UIColor whiteColor];
    noResultsLabel_.backgroundColor = [UIColor clearColor];
    noResultsLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.4];
    noResultsLabel_.shadowOffset = CGSizeMake(0, -1);
    noResultsLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:11];
    noResultsLabel_.frame = CGRectOffset(noResultsLabel_.frame, 15, 12);
    [self addSubview:noResultsLabel_];
    [noResultsLabel_ release];
    self.alpha = 0;
  }
  return self;
}

- (void)dealloc {
  indicatorView_ = nil;
  noResultsLabel_ = nil;
  [super dealloc];
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  backgroundImageView_.frame = self.bounds;
}

- (void)setMode:(STMapIndicatorViewMode)mode {
  mode_ = mode;
  
  switch (mode) {
    case STMapIndicatorViewModeHidden: {
      [UIView animateWithDuration:0.3
                            delay:0
                          options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                       animations:^{ self.alpha = 0.0; }
                       completion:^(BOOL finished) {
                         [indicatorView_ performSelectorOnMainThread:@selector(stopAnimating) withObject:nil waitUntilDone:NO];
                         noResultsLabel_.alpha = 0.0;
                       }];
      break;
    }
    case STMapIndicatorViewModeLoading: {
      CGRect frame = self.frame;
      frame.size.width = 44;
      if (((CALayer*)self.layer.presentationLayer).opacity == 0) {
        self.frame = frame;
        noResultsLabel_.alpha = 0.0;
      }

      [indicatorView_ startAnimating];

      [UIView animateWithDuration:0.3
                            delay:0
                          options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                       animations:^{
                         self.frame = frame;
                         self.alpha = 1.0;
                         noResultsLabel_.alpha = 0.0;
                       }
                       completion:nil];
      break;
    }
    case STMapIndicatorViewModeNoConnection:
    case STMapIndicatorViewModeNoResults: {
      noResultsLabel_.text = (mode == STMapIndicatorViewModeNoConnection) ? NSLocalizedString(@"No connection", nil) : NSLocalizedString(@"No results", nil);
      [noResultsLabel_ sizeToFit];
      CGRect frame = self.frame;
      frame.size.width = CGRectGetWidth(noResultsLabel_.bounds) + 30;

      if (((CALayer*)self.layer.presentationLayer).opacity == 0)
        self.frame = frame;
      
      [indicatorView_ stopAnimating];
      [UIView animateWithDuration:0.3
                            delay:0
                          options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                       animations:^{
                         self.frame = frame;
                         self.alpha = 1.0;
                         noResultsLabel_.alpha = 1.0;
                       } completion:nil];
      break;
    }
    
    default:
      break;
  }
}

@end
