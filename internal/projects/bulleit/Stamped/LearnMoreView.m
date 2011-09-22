//
//  LearnMoreView.m
//  Stamped
//
//  Created by Jake Zien on 9/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "LearnMoreView.h"

@interface LearnMoreView ()


@end

static CGFloat const kSlide0X = 0;
static CGFloat const kSlide1X = 380;
static CGFloat const kSlide2X = 760;
static CGFloat const kSlide3X = 1140;
static CGFloat const kSlide4X = 1520;
static CGFloat const kSlideWidth = 380;

@implementation LearnMoreView


@synthesize scrollView;


- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) { }
  return self;
}

- (void)dealloc {
  self.scrollView.delegate = nil;
}

- (void)awakeFromNib {
  
  
  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"],
                       [UIImage imageNamed:@"learnmore_01_stars"],
                       [UIImage imageNamed:@"learnmore_02_stamp"],
                       [UIImage imageNamed:@"learnmore_03"],
                       [UIImage imageNamed:@"learnmore_04_stamps"], nil];
  
  for (NSUInteger i = 0; i < bgImages.count; ++i) {
    UIImageView* subview = [[UIImageView alloc] initWithImage:[bgImages objectAtIndex:i]];
    
    CGRect frame = self.scrollView.frame;
    frame.origin.x = CGRectGetWidth(frame) * i;
    subview.frame = frame;
    subview.clipsToBounds = NO;
    subview.contentMode = UIViewContentModeCenter;
        
    [self.scrollView addSubview:subview];
    
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(CGRectGetWidth(self.scrollView.frame) * bgImages.count,
                                           CGRectGetHeight(self.scrollView.frame)); 
  
  
}





@end