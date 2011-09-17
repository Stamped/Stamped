//
//  LearnMoreView.m
//  Stamped
//
//  Created by Jake Zien on 9/14/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "LearnMoreView.h"
#import "LearnMoreChoreographer.h"

@interface LearnMoreView ()

- (void)setupSlide:(UIImageView*)imageView;


@end


@implementation LearnMoreView


@synthesize scrollView;
@synthesize choreographer = choreographer_;


- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) { }
  return self;
}

- (void)dealloc {
  self.scrollView.delegate = nil;
  [choreographer_ release];
}

- (void)awakeFromNib {
  
  choreographer_ = [[LearnMoreChoreographer alloc] init];
//  self.scrollView.delegate = self.choreographer;
  
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
    subview.clipsToBounds = YES;
    subview.contentMode = UIViewContentModeCenter;
    
    [self.scrollView addSubview:subview];
    
    if (i==1)   [self setupSlide:subview];
    
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(CGRectGetWidth(self.scrollView.frame) * bgImages.count,
                                           CGRectGetHeight(self.scrollView.frame));  
  
//  NSLog(@"%@", self.choreographer);

  
}


- (void)setupSlide:(UIView*)view {
  /*
  UIImage* starImg = [UIImage imageNamed:@"learnmore_star"];
  
  for (NSUInteger i = 0; i < 5; ++i) {
    UIImageView* starView = [[UIImageView alloc] initWithImage:starImg];
    CGRect frame = CGRectMake(26 + (i * starImg.size.width - 12), 95, starImg.size.width, starImg.size.height);
    starView.frame = frame;
    starView.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.5];
    [view addSubview:starView];

    if (i==2)
    [self.choreographer addChoreographyForView:starView
                                         range:NSMakeRange(1, 419)
                                      property:@"frame.origin.y"
                                    startValue:[NSNumber numberWithInt:4]
                                      endValue:[NSNumber numberWithInt:10]];
    
    [starView release];
   
  } */ 
}


@end