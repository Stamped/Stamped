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
#import "Notifications.h"
#import "TodoViewController.h"
#import "PeopleViewController.h"
#import "STNavigationBar.h"
#import "STSearchField.h"
#import "Util.h"

#warning delete this mofo
#import "WelcomeViewController.h"


@interface RootTabBarViewController ()
- (void)finishViewInit;
- (void)fillStampImageView;
- (void)ensureCorrectHeightOfViewControllers;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)newsCountChanged:(NSNotification*)notification;
- (void)reloadPanes:(NSNotification*)notification;
- (void)tooltipTapped:(UITapGestureRecognizer*)recognizer;

@property (nonatomic, readonly) UIImageView* tooltipImageView;

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
@synthesize userStampBackgroundImageView = userStampBackgroundImageView_;
@synthesize tooltipImageView = tooltipImageView_;

- (void)dealloc {
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
  self.userStampBackgroundImageView = nil;
  tooltipImageView_ = nil;
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(currentUserUpdated:)
                                               name:kCurrentUserHasUpdatedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(newsCountChanged:)
                                               name:kNewsItemCountHasChangedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(reloadPanes:)
                                               name:kAppShouldReloadAllPanes
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(reloadPanes:)
                                               name:UIApplicationSignificantTimeChangeNotification
                                             object:nil];
  

  [AccountManager sharedManager].delegate = self;
  if ([AccountManager sharedManager].authenticated) {
    [self finishViewInit];
  } else {
    [[AccountManager sharedManager] authenticate];
  }

  if ([AccountManager sharedManager].currentUser)
    [self fillStampImageView];
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
  
#warning delete this mofo.
  WelcomeViewController* vc = [[WelcomeViewController alloc] init];
  [self presentModalViewController:vc animated:YES];
  [vc release];
}

- (void)ensureCorrectHeightOfViewControllers {
  for (UIViewController* controller in self.viewControllers) {
    controller.view.frame =
        CGRectMake(0, 0, 320, CGRectGetHeight(self.view.frame) - CGRectGetHeight(self.tabBar.frame));
  }
}

- (void)currentUserUpdated:(NSNotification*)notification {
  [self fillStampImageView];
}

- (void)fillStampImageView {
  User* user = [AccountManager sharedManager].currentUser;
  
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:user.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (user.secondaryColor) {
    [Util splitHexString:user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }

  CGFloat width = userStampBackgroundImageView_.frame.size.width;
  CGFloat height = userStampBackgroundImageView_.frame.size.height;
  
  UIGraphicsBeginImageContextWithOptions(userStampBackgroundImageView_.frame.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();

  CGFloat colors[] = {r1, g1, b1, 1.0,  r2, g2, b2, 1.0};
  CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
  CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
  CGPoint gradientStartPoint = CGPointZero;
  CGPoint gradientEndPoint = CGPointMake(width, height);
  CGContextDrawLinearGradient(context,
                              gradientRef,
                              gradientStartPoint,
                              gradientEndPoint,
                              kCGGradientDrawsAfterEndLocation);
  CGGradientRelease(gradientRef);
  CGColorSpaceRelease(colorSpace);
  userStampBackgroundImageView_.image = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  [userStampBackgroundImageView_ setNeedsDisplay];
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
  self.userStampBackgroundImageView = nil;
  tooltipImageView_ = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.selectedViewController viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.selectedViewController viewDidAppear:animated];

  if (![[NSUserDefaults standardUserDefaults] boolForKey:@"hasStamped"]) {
    if (!tooltipImageView_) {
      tooltipImageView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"tooltip_stampit"]];
      tooltipImageView_.frame = CGRectOffset(tooltipImageView_.frame,
          (CGRectGetWidth(self.view.frame) - CGRectGetWidth(tooltipImageView_.frame)) / 2, 245);
      tooltipImageView_.alpha = 0.0;
      tooltipImageView_.userInteractionEnabled = YES;
      UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                                   action:@selector(tooltipTapped:)];
      [tooltipImageView_ addGestureRecognizer:recognizer];
      [recognizer release];
      [self.view addSubview:tooltipImageView_];
      [tooltipImageView_ release];
    }

    if (self.selectedViewController == [viewControllers_ objectAtIndex:0])
      [UIView animateWithDuration:0.3
                            delay:1.0
                          options:UIViewAnimationOptionAllowUserInteraction
                       animations:^{ tooltipImageView_.alpha = 1.0; }
                       completion:nil];
  }
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [self.selectedViewController viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  [self.selectedViewController viewDidDisappear:animated];

  if (tooltipImageView_) {
    tooltipImageView_.alpha = 0.0;
    [tooltipImageView_ removeFromSuperview];
    tooltipImageView_ = nil;
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"hasStamped"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)tooltipTapped:(UITapGestureRecognizer*)recognizer {
  if (tooltipImageView_) {
    [UIView animateWithDuration:0.3 
                          delay:0 
                        options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                     animations:^{ tooltipImageView_.alpha = 0.0; }
                     completion:^(BOOL finished) {
                       [tooltipImageView_ removeFromSuperview];
                       tooltipImageView_ = nil;
                     }];
    [[NSUserDefaults standardUserDefaults] setBool:YES forKey:@"hasStamped"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }
}

- (IBAction)createStamp:(id)sender {
  [self.searchStampsNavigationController popToRootViewControllerAnimated:NO];
  SearchEntitiesViewController* vc = (SearchEntitiesViewController*)[searchStampsNavigationController_.viewControllers objectAtIndex:0];
  [vc clearSearchField];
  [self presentModalViewController:self.searchStampsNavigationController animated:YES];
}

- (void)stampWasCreated:(NSNotification*)notification {
  if (self.tabBar.selectedItem != mustDoTabBarItem_) {
    self.tabBar.selectedItem = stampsTabBarItem_;
    [self tabBar:self.tabBar didSelectItem:stampsTabBarItem_];
  }
}

- (void)newsCountChanged:(NSNotification*)notification {
  NSNumber* newItemCount = notification.object;
  NSLog(@"Setting news item count to %@", newItemCount);
  if (self.tabBar.selectedItem != activityTabBarItem_)
    activityTabBarItem_.badgeValue = [newItemCount stringValue];
}

- (void)reloadPanes:(NSNotification*)notification {
  for (STReloadableTableViewController* viewController in self.viewControllers) {
    if (notification.object != viewController)
      [viewController reloadData];
  }
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
    self.navigationItem.title = @"News";
    activityTabBarItem_.badgeValue = nil;
  } else if (item == mustDoTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:2];
    self.navigationItem.title = @"To Do";
  } else if (item == peopleTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:3];
    self.navigationItem.title = @"People";
  }
  
  [self.navigationController.navigationBar setNeedsDisplay];

  if (!newViewController || newViewController == self.selectedViewController)
    return;

  [self.selectedViewController viewWillDisappear:NO];
  [self.selectedViewController.view removeFromSuperview];
  [self.selectedViewController viewDidDisappear:NO];
  [newViewController viewWillAppear:NO];
  [self ensureCorrectHeightOfViewControllers];
  [self.view insertSubview:newViewController.view atIndex:0];
  [newViewController viewDidAppear:NO];
  self.selectedViewController = newViewController;
}

@end
