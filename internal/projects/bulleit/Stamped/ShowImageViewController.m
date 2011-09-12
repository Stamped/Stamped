//
//  ShowImageViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ShowImageViewController.h"

@interface ShowImageViewController ()
- (void)handleImageTap:(UITapGestureRecognizer*)recognizer;
@end

@implementation ShowImageViewController

@synthesize imageView = imageView_;
@synthesize image = image_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.image = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:NO animated:animated];
  [super viewWillDisappear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  
  self.imageView.image = image_;
  UITapGestureRecognizer* recognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self
                                              action:@selector(handleImageTap:)];
  [self.imageView addGestureRecognizer:recognizer];
  [recognizer release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.imageView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Tapping N' Bullshit.

- (void)handleImageTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;
  
  BOOL isHidden = self.navigationController.navigationBarHidden;
  [self.navigationController setNavigationBarHidden:!isHidden animated:YES];
}

#pragma mark - UIScrollViewDelegate Methods.

- (UIView*)viewForZoomingInScrollView:(UIScrollView*)scrollView {
  return imageView_;
}

@end
