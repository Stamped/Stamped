//
//  RootTabBarViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "RootTabBarViewController.h"

#import "StampsListViewController.h"
#import "ActivityViewController.h"

@implementation RootTabBarViewController

@synthesize viewControllers = viewControllers_;
@synthesize selectedViewController = selectedViewController_;
@synthesize addStampButton = addStampButton_;
@synthesize tabBar = tabBar_;
@synthesize stampsTabBarItem = stampsTabBarItem_;
@synthesize activityTabBarItem = activityTabBarItem_;
@synthesize mustDoTabBarItem = mustDoTabBarItem_;
@synthesize peopleTabBarItem = peopleTabBarItem_;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {}
  return self;
}

- (void)dealloc {
  self.selectedViewController = nil;
  self.viewControllers = nil;
  self.tabBar = nil;
  self.addStampButton = nil;
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
  // Do this so that there is no title shown.
  self.navigationItem.titleView = [[[UIView alloc] initWithFrame:CGRectZero] autorelease];

  StampsListViewController* stampsList = [[StampsListViewController alloc]
      initWithNibName:@"StampsListViewController" bundle:nil];
  ActivityViewController* activity = [[ActivityViewController alloc]
      initWithNibName:@"ActivityViewController" bundle:nil];
  self.viewControllers = [NSArray arrayWithObjects:stampsList, activity, nil];
  
  [self.view addSubview:stampsList.view];
  self.selectedViewController = stampsList;  
  [stampsList release];
  [activity release];

  self.tabBar.selectedItem = stampsTabBarItem_;

  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.selectedViewController = nil;
  self.viewControllers = nil;
  self.tabBar = nil;
  self.addStampButton = nil;
  self.stampsTabBarItem = nil;
  self.activityTabBarItem = nil;
  self.mustDoTabBarItem = nil;
  self.peopleTabBarItem = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITabBarDelegate Methods

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

  [self.selectedViewController.view removeFromSuperview];
  [self.view addSubview:newViewController.view];
  self.selectedViewController = newViewController;
}

@end
