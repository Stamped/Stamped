//
//  RootTabBarViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "RootTabBarViewController.h"

#import "InboxViewController.h"
#import "ActivityViewController.h"
#import "CreateStampViewController.h"

@interface RootTabBarViewController ()
- (void)finishViewInit;
@end

@implementation RootTabBarViewController

@synthesize viewControllers = viewControllers_;
@synthesize selectedViewController = selectedViewController_;
@synthesize tabBar = tabBar_;
@synthesize stampsTabBarItem = stampsTabBarItem_;
@synthesize activityTabBarItem = activityTabBarItem_;
@synthesize mustDoTabBarItem = mustDoTabBarItem_;
@synthesize peopleTabBarItem = peopleTabBarItem_;

- (void)dealloc {
  self.selectedViewController = nil;
  self.viewControllers = nil;
  self.tabBar = nil;
  self.stampsTabBarItem = nil;
  self.activityTabBarItem = nil;
  self.mustDoTabBarItem = nil;
  self.peopleTabBarItem = nil;

  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];

  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  // Do this so that there is no title shown.
  self.navigationItem.titleView = [[[UIView alloc] initWithFrame:CGRectZero] autorelease];
  [AccountManager sharedManager].delegate = self;
  [[AccountManager sharedManager] authenticate];
}

- (void)finishViewInit {
  InboxViewController* inbox = [[InboxViewController alloc] initWithNibName:@"InboxViewController" bundle:nil];
  ActivityViewController* activity = [[ActivityViewController alloc] initWithNibName:@"ActivityViewController" bundle:nil];
  self.viewControllers = [NSArray arrayWithObjects:inbox, activity, nil];
  CGRect inboxFrame = CGRectMake(0, 0, 320, CGRectGetHeight(self.view.frame) - CGRectGetHeight(self.tabBar.frame));
  inbox.view.frame = inboxFrame;
  [self.view addSubview:inbox.view];
  self.selectedViewController = inbox;  
  [inbox release];
  [activity release];
  if ([self.tabBar respondsToSelector:@selector(setSelectedImageTintColor:)])
    [self.tabBar setSelectedImageTintColor:[UIColor colorWithWhite:0.9 alpha:1.0]];
  
  self.tabBar.selectedItem = stampsTabBarItem_;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.selectedViewController = nil;
  self.viewControllers = nil;
  self.tabBar = nil;
  self.stampsTabBarItem = nil;
  self.activityTabBarItem = nil;
  self.mustDoTabBarItem = nil;
  self.peopleTabBarItem = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.selectedViewController viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.selectedViewController viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [self.selectedViewController viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  [self.selectedViewController viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)createStamp:(id)sender {
  CreateStampViewController* createStampViewController =
      [[CreateStampViewController alloc] initWithNibName:@"CreateStampViewController" bundle:nil];
  UINavigationController* createStampNavController = [[UINavigationController alloc] initWithRootViewController:createStampViewController];
  [createStampViewController release];
  createStampNavController.navigationBarHidden = YES;
  [self presentModalViewController:createStampNavController animated:YES];
  [createStampNavController release];
}

#pragma mark - AccountManagerDelegate Methods.

- (void)accountManagerDidAuthenticate {
  [self finishViewInit];
}

#pragma mark - UITabBarDelegate Methods.

- (void)tabBar:(UITabBar*)tabBar didSelectItem:(UITabBarItem*)item {
  UIViewController* newViewController = nil;
  if (item == stampsTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:0];
    self.navigationItem.title = @"Stamps";
  } else if (item == activityTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:1];
    self.navigationItem.title = @"Activity";
  }
  if (!newViewController || newViewController == self.selectedViewController)
    return;

  [self.selectedViewController viewWillDisappear:NO];
  [self.selectedViewController.view removeFromSuperview];
  [self.selectedViewController viewDidDisappear:NO];
  [newViewController viewWillAppear:NO];
  [self.view addSubview:newViewController.view];
  [newViewController viewDidAppear:NO];
  self.selectedViewController = newViewController;
}

@end
