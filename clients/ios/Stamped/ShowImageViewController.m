//
//  ShowImageViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ShowImageViewController.h"

#import "STImageView.h"
#import "STNavigationBar.h"

@interface ShowImageViewController ()
- (void)handleImageTap:(UITapGestureRecognizer*)recognizer;
@end

@implementation ShowImageViewController

@synthesize imageView = imageView_;
@synthesize image = image_;
@synthesize imageURL = imageURL_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.imageView = nil;
  self.image = nil;
  self.imageURL = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [[UIApplication sharedApplication] setStatusBarStyle:UIStatusBarStyleBlackTranslucent];
  //[[UIApplication sharedApplication] setStatusBarHidden:YES withAnimation:UIStatusBarAnimationSlide];
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  self.navigationController.navigationBar.translucent = YES;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  navBar.black = YES;
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [[UIApplication sharedApplication] setStatusBarStyle:UIStatusBarStyleBlackOpaque];
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  navBar.black = NO;
  self.navigationController.navigationBar.translucent = NO;
  //[self.navigationController setNavigationBarHidden:NO animated:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.wantsFullScreenLayout = YES;
  self.view.backgroundColor = [UIColor blackColor];
  self.imageView.backgroundColor = [UIColor blackColor];

  if (image_)
    self.imageView.image = image_;
  else if (imageURL_)
    self.imageView.imageURL = imageURL_;

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
  [[UIApplication sharedApplication] setStatusBarHidden:!isHidden withAnimation:UIStatusBarAnimationFade];
  [self.navigationController setNavigationBarHidden:!isHidden animated:YES];
  
}

#pragma mark - UIScrollViewDelegate Methods.

- (UIView*)viewForZoomingInScrollView:(UIScrollView*)scrollView {
  return imageView_;
}

@end
