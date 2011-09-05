//
//  FirstRunViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import "FirstRunViewController.h"

@interface FirstRunViewController ()
- (void)setupBottomView;
- (void)setupSlide:(UIImageView*)imageView;
@end

@implementation FirstRunViewController

@synthesize scrollView = scrollView_;
@synthesize bottomView = bottomView_;
@synthesize animView = animView_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  [self setupBottomView];

  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"],
                                                [UIImage imageNamed:@"learnmore_01"],
                                                [UIImage imageNamed:@"learnmore_02"],
                                                [UIImage imageNamed:@"learnmore_03"],
                                                [UIImage imageNamed:@"learnmore_04"], nil];
  
  for (NSUInteger i = 0; i < bgImages.count; ++i) {
    CGRect frame = self.scrollView.frame;
    frame.origin.x = self.scrollView.frame.size.width * i;
    
    UIImageView* subview = [[UIImageView alloc] initWithFrame:frame];
    subview.image = [bgImages objectAtIndex:i];
    subview.clipsToBounds = YES;
    subview.contentMode = UIViewContentModeRight;
    
    if (i == 1)
      [self setupSlide:subview];

    [self.scrollView addSubview:subview];
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(CGRectGetWidth(self.scrollView.frame) * bgImages.count,
                                           CGRectGetHeight(self.scrollView.frame));
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.bottomView = nil;
  self.scrollView = nil;
  self.animView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Setup Views

- (void)setupBottomView {
  CAGradientLayer* bottomGradient = [[CAGradientLayer alloc] init];
  bottomGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.88 alpha:1.0].CGColor, nil];
  bottomGradient.frame = bottomView_.bounds;
  
  
  [bottomView_.layer insertSublayer:bottomGradient atIndex:0];
  [bottomGradient release];
}


- (void)setupSlide:(UIImageView*)imageView {
  UIImage* starImg = [UIImage imageNamed:@"learnmore_star"];

  for (NSUInteger i = 0; i < 5; ++i) {
    UIImageView* starView = [[UIImageView alloc] initWithImage:starImg];
    CGRect frame = CGRectMake(26 + (i * starImg.size.width - 12), 95, starImg.size.width, starImg.size.height);
    starView.frame = frame;
    starView.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.5];
    [imageView addSubview:starView];
    [starView release];
  }
}


@end
