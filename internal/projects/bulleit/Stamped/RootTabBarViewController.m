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
#import "PeopleViewController.h"
#import "STNavigationBar.h"
#import "STSearchField.h"
#import "Util.h"

@interface RootTabBarViewController ()
- (void)finishViewInit;
- (void)fillStampImageView;
- (void)setTabBarIcons;
- (void)ensureCorrectHeightOfViewControllers;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)currentUserUpdated:(NSNotification*)notification;
- (void)newsCountChanged:(NSNotification*)notification;
- (void)reloadPanes:(NSNotification*)notification;
- (void)userLoggedOut:(NSNotification*)notification;
- (void)tooltipTapped:(UITapGestureRecognizer*)recognizer;
- (void)pushNotificationReceived:(NSNotification*)notification;

@property (nonatomic, readonly) UIImageView* tooltipImageView;
@property (nonatomic, copy) NSArray* tabBarItems;
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
@synthesize tabBarItems = tabBarItems_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [AccountManager sharedManager].delegate = nil;
  self.searchStampsNavigationController = nil;
  self.selectedViewController = nil;
  self.tabBarItems = nil;
  self.viewControllers = nil;
  self.tabBar = nil;
  self.stampsTabBarItem = nil;
  self.activityTabBarItem = nil;
  self.mustDoTabBarItem = nil;
  self.peopleTabBarItem = nil;
  self.userStampBackgroundImageView = nil;
  tooltipImageView_ = nil;
  ((TodoViewController*)[self.viewControllers objectAtIndex:2]).delegate = nil;
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
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(userLoggedOut:)
                                               name:kUserHasLoggedOutNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(pushNotificationReceived:)
                                               name:kPushNotificationReceivedNotification
                                             object:nil];

  [AccountManager sharedManager].delegate = self;
  if ([AccountManager sharedManager].authenticated) {
    [self finishViewInit];
  } else {
    [[AccountManager sharedManager] authenticate];
  }

  if ([AccountManager sharedManager].currentUser)
    [self fillStampImageView];
  
  [self setTabBarIcons];
}

- (void)finishViewInit {
  [[UIApplication sharedApplication] registerForRemoteNotificationTypes:UIRemoteNotificationTypeBadge |
                                                                        UIRemoteNotificationTypeAlert];
  
  InboxViewController* inbox = [[InboxViewController alloc] initWithNibName:@"InboxViewController" bundle:nil];
  ActivityViewController* activity = [[ActivityViewController alloc] initWithNibName:@"ActivityViewController" bundle:nil];
  TodoViewController* todo = [[TodoViewController alloc] initWithNibName:@"TodoViewController" bundle:nil];
  PeopleViewController* people = [[PeopleViewController alloc] initWithNibName:@"PeopleViewController" bundle:nil];

  todo.delegate = self;

  self.viewControllers = [NSArray arrayWithObjects:inbox, activity, todo, people, nil];
  [inbox release];
  [activity release];
  [todo release];
  [people release];

  self.tabBarItems = [NSArray arrayWithObjects:stampsTabBarItem_,
                                               activityTabBarItem_,
                                               mustDoTabBarItem_,
                                               peopleTabBarItem_,
                                               nil];
  
  // This will load all views.
  [self ensureCorrectHeightOfViewControllers];
  if (!self.tabBar.selectedItem) {
    self.tabBar.selectedItem = [tabBarItems_ objectAtIndex:selectedViewControllerIndex_];
    [self tabBar:self.tabBar didSelectItem:self.tabBar.selectedItem];
  }
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

- (void)userLoggedOut:(NSNotification*)notification {
  activityTabBarItem_.badgeValue = nil;
  selectedViewControllerIndex_ = 0;
  self.tabBar.selectedItem = [tabBarItems_ objectAtIndex:selectedViewControllerIndex_];
  [self tabBar:self.tabBar didSelectItem:self.tabBar.selectedItem];
  [self.selectedViewController.view removeFromSuperview];
  self.tabBar.selectedItem = nil;
}

- (void)setTabBarIcons {
  if (![stampsTabBarItem_ respondsToSelector:@selector(setFinishedSelectedImage:withFinishedUnselectedImage:)])
    return;
  [stampsTabBarItem_ setFinishedSelectedImage:[UIImage imageNamed:@"tab_stamps_button_active"]
                  withFinishedUnselectedImage:[UIImage imageNamed:@"tab_stamps_button"]];
  [activityTabBarItem_ setFinishedSelectedImage:[UIImage imageNamed:@"tab_news_button_active"]
                    withFinishedUnselectedImage:[UIImage imageNamed:@"tab_news_button"]];
  [mustDoTabBarItem_ setFinishedSelectedImage:[UIImage imageNamed:@"tab_todo_button_active"]
                  withFinishedUnselectedImage:[UIImage imageNamed:@"tab_todo_button"]];
  [peopleTabBarItem_ setFinishedSelectedImage:[UIImage imageNamed:@"tab_people_button_active"]
                  withFinishedUnselectedImage:[UIImage imageNamed:@"tab_people_button"]];
  self.tabBar.backgroundImage = [UIImage imageNamed:@"tab_bar_bg"];
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
  self.tabBarItems = nil;
  self.tabBar = nil;
  self.stampsTabBarItem = nil;
  self.activityTabBarItem = nil;
  self.mustDoTabBarItem = nil;
  self.peopleTabBarItem = nil;
  self.userStampBackgroundImageView = nil;
  tooltipImageView_ = nil;
  ((TodoViewController*)[self.viewControllers objectAtIndex:2]).delegate = nil;
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
  vc.searchIntent = SearchIntentStamp;
  [vc resetState];
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

- (void)pushNotificationReceived:(NSNotification*)notification {
  if ([UIApplication sharedApplication].applicationState != UIApplicationStateActive) {
    self.tabBar.selectedItem = activityTabBarItem_;
    [self tabBar:self.tabBar didSelectItem:activityTabBarItem_];
  }
  [((ActivityViewController*)[self.viewControllers objectAtIndex:1]) reloadData];
}

#pragma mark - AccountManagerDelegate Methods.

- (void)accountManagerDidAuthenticate {
  [self finishViewInit];
}

#pragma mark - TodoViewControllerDelegate Methods.

- (void)displaySearchEntities {
  [self.searchStampsNavigationController popToRootViewControllerAnimated:NO];
  [self.searchStampsNavigationController setNavigationBarHidden:YES];
  SearchEntitiesViewController* vc = (SearchEntitiesViewController*)[searchStampsNavigationController_.viewControllers objectAtIndex:0];
  vc.searchIntent = SearchIntentTodo;
  [vc resetState];
  [self presentModalViewController:self.searchStampsNavigationController animated:YES];
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
  selectedViewControllerIndex_ = [tabBarItems_ indexOfObject:item];
}

@end
