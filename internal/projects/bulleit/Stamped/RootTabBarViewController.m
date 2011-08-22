//
//  RootTabBarViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "RootTabBarViewController.h"

#import "Stamp.h"
#import "InboxViewController.h"
#import "ActivityViewController.h"
#import "SearchEntitiesViewController.h"
#import "TodoViewController.h"
#import "PeopleViewController.h"
#import "STNavigationBar.h"

@interface RootTabBarViewController ()
- (void)finishViewInit;
- (void)ensureCorrectHeightOfViewControllers;
- (void)stampWasCreated:(NSNotification*)notification;
@end

@implementation RootTabBarViewController

@synthesize searchStampsNavigationController = searchStampsNavigationController_;
@synthesize viewControllers = viewControllers_;
@synthesize selectedViewController = selectedViewController_;
@synthesize tabBar = tabBar_;
@synthesize stampsTabBarItem = stampsTabBarItem_;
@synthesize activityTabBarItem = activityTabBarItem_;
@synthesize mustDoTabBarItem = mustDoTabBarItem_;
@synthesize peopleTabBarItem = peopleTabBarItem_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.searchStampsNavigationController = nil;
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(stampWasCreated:)
                                               name:kStampWasCreatedNotification
                                             object:nil];
  [AccountManager sharedManager].delegate = self;
  if ([AccountManager sharedManager].authenticated) {
    [self finishViewInit];
  } else {
    [[AccountManager sharedManager] authenticate];
  }
}

- (void)finishViewInit {
  InboxViewController* inbox = [[InboxViewController alloc] initWithNibName:@"InboxViewController" bundle:nil];
  ActivityViewController* activity = [[ActivityViewController alloc] initWithNibName:@"ActivityViewController" bundle:nil];
  TodoViewController* todo = [[TodoViewController alloc] initWithNibName:@"TodoViewController" bundle:nil];
  PeopleViewController* people = [[PeopleViewController alloc] initWithNibName:@"PeopleViewController" bundle:nil];
  self.viewControllers = [NSArray arrayWithObjects:inbox, activity, todo, people, nil];
  [inbox release];
  [activity release];
  [todo release];
  [people release];

  // This will load all views.
  [self ensureCorrectHeightOfViewControllers];
  if (!self.tabBar.selectedItem) {
    self.tabBar.selectedItem = stampsTabBarItem_;
    [self tabBar:self.tabBar didSelectItem:stampsTabBarItem_];
  }
}

- (void)ensureCorrectHeightOfViewControllers {
  for (UIViewController* controller in self.viewControllers) {
    controller.view.frame =
        CGRectMake(0, 0, 320, CGRectGetHeight(self.view.frame) - CGRectGetHeight(self.tabBar.frame));
  }
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [AccountManager sharedManager].delegate = nil;
  self.searchStampsNavigationController = nil;
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
  [self.searchStampsNavigationController popToRootViewControllerAnimated:NO];
  [self presentModalViewController:self.searchStampsNavigationController animated:YES];
}

- (void)stampWasCreated:(NSNotification*)notification {
  self.tabBar.selectedItem = stampsTabBarItem_;
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
  } else if (item == mustDoTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:2];
    self.navigationItem.title = @"Todo";
  } else if (item == peopleTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:3];
    self.navigationItem.title = @"People";
  }
    
  if (!newViewController || newViewController == self.selectedViewController)
    return;

  [self.selectedViewController viewWillDisappear:NO];
  [self.selectedViewController.view removeFromSuperview];
  [self.selectedViewController viewDidDisappear:NO];
  [newViewController viewWillAppear:NO];
  [self ensureCorrectHeightOfViewControllers];
  [self.view addSubview:newViewController.view];
  [newViewController viewDidAppear:NO];
  self.selectedViewController = newViewController;
}

@end
