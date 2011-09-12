//
//  WelcomeViewController.m
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import "WelcomeViewController.h"

#import "FindFriendsViewController.h"
#import "StampedAppDelegate.h"

@implementation WelcomeViewController

@synthesize contentView = contentView_;
@synthesize scrollView = scrollView_;
@synthesize pageControl = pageControl_;

@synthesize page1Title = page1Title_;
@synthesize page2Title = page2Title_;
@synthesize page3Title = page3Title_;

- (id)init {
  if ((self = [self initWithNibName:@"WelcomeView" bundle:nil])) {
  }
  return self;
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  [self.scrollView addSubview:self.contentView];
  self.scrollView.contentSize = self.contentView.frame.size;

  UIFont* font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36.0];
  self.page1Title.font = font;
  self.page2Title.font = font;
  self.page3Title.font = font;
}

- (void)viewDidUnload {
  self.contentView = nil;
  self.scrollView = nil;
  self.pageControl = nil;
  self.page1Title = nil;
  self.page2Title = nil;
  self.page3Title = nil;
  [super viewDidUnload];
}

#pragma mark - Actions

- (IBAction)findfromContacts:(id)sender {
  FindFriendsViewController* findFriendsVC = [[FindFriendsViewController alloc] initWithFindSource:FindFriendsFromContacts];
  [self.navigationController pushViewController:findFriendsVC animated:YES];
  [findFriendsVC release];
}

- (IBAction)findFromTwitter:(id)sender {
  FindFriendsViewController* findFriendsVC = [[FindFriendsViewController alloc] initWithFindSource:FindFriendsFromTwitter];
  [self.navigationController pushViewController:findFriendsVC animated:YES];
  [findFriendsVC release];
}

- (IBAction)dismissWelcomeView:(id)sender {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[UIApplication sharedApplication].delegate;
  [delegate.navigationController dismissModalViewControllerAnimated:YES];
}

- (IBAction)pageViewChanged:(id)sender {
  NSInteger page = self.pageControl.currentPage;

  // The scroll view contains a single view whose contents each are the width of
  // the containing scroll view.
  CGFloat xOffset = self.scrollView.frame.size.width * page;
  CGPoint offset = CGPointMake(xOffset, 0);

  [self.scrollView setContentOffset:offset animated:YES];
}

#pragma mark - Scroll View Delegate

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  CGFloat xOffset = self.scrollView.contentOffset.x;
  NSInteger page = xOffset / self.scrollView.frame.size.width;
  self.pageControl.currentPage = page;
}

@end
