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
- (void)overlayWasTapped:(UIGestureRecognizer*)recognizer;

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
  self.tabBar.delegate = nil;
  self.tabBar = nil;
  self.tabBarItems = nil;
  ((TodoViewController*)[self.viewControllers objectAtIndex:2]).delegate = nil;
  self.viewControllers = nil;
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
    controller.view.frame = CGRectMake(0, 0, 320, 367);
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
  [[NSUserDefaults standardUserDefaults] setBool:NO forKey:@"hasStamped"];
  [[NSUserDefaults standardUserDefaults] synchronize];
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

  UIGraphicsBeginImageContextWithOptions(userStampBackgroundImageView_.frame.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();
  [[UIColor blackColor] setFill];
  CGContextFillRect(context, userStampBackgroundImageView_.bounds);
  UIImage* mask = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  userStampBackgroundImageView_.image = [Util gradientImage:mask
                                           withPrimaryColor:user.primaryColor
                                                  secondary:user.secondaryColor];
  [userStampBackgroundImageView_ setNeedsDisplay];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [AccountManager sharedManager].delegate = nil;
  self.tabBar.delegate = nil;
  self.tabBar = nil;
  self.searchStampsNavigationController = nil;
  self.selectedViewController = nil;
  ((TodoViewController*)[self.viewControllers objectAtIndex:2]).delegate = nil;
  self.tabBarItems = nil;
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

  if ([[NSUserDefaults standardUserDefaults] boolForKey:@"firstStamp"]) {
    UIView* overlayContainer = [[UIView alloc] initWithFrame:self.view.window.frame];
    overlayContainer.backgroundColor = [UIColor clearColor];
    overlayContainer.alpha = 0;
    UIView* black = [[UIView alloc] initWithFrame:overlayContainer.bounds];
    black.backgroundColor = [UIColor blackColor];
    black.alpha = 0.75;
    [overlayContainer addSubview:black];
    [black release];
    UIImageView* earnMore = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"earn_tip_1stStamp"]];
    earnMore.center = overlayContainer.center;
    [overlayContainer addSubview:earnMore];
    [earnMore release];
    User* currentUser = [AccountManager sharedManager].currentUser;
    UIImageView* creditLeft = [[UIImageView alloc] initWithImage:[Util gradientImage:[UIImage imageNamed:@"stamp_28pt_texture"]
                                                                    withPrimaryColor:currentUser.primaryColor
                                                                           secondary:currentUser.secondaryColor]];
    creditLeft.frame = CGRectOffset(creditLeft.frame, 62, 75);
    [earnMore addSubview:creditLeft];
    [creditLeft release];
    UIImageView* creditRight = [[UIImageView alloc] initWithImage:[Util gradientImage:[UIImage imageNamed:@"stamp_28pt_solid"]
                                                                    withPrimaryColor:currentUser.primaryColor
                                                                           secondary:currentUser.secondaryColor]];
    creditRight.frame = CGRectOffset(creditLeft.frame, 14, 0);
    [earnMore addSubview:creditRight];
    [creditRight release];
    UIImageView* creditOverlay = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_28pt_overlaySolid"]];
    creditOverlay.center = creditRight.center;
    [earnMore addSubview:creditOverlay];
    [creditOverlay release];
    UITapGestureRecognizer* recognizer =
        [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(overlayWasTapped:)];
    [overlayContainer addGestureRecognizer:recognizer];
    [recognizer release];
    [self.view.window addSubview:overlayContainer];
    [UIView animateWithDuration:0.3 animations:^{
      overlayContainer.alpha = 1;
    }];
    [overlayContainer release];
    [[NSUserDefaults standardUserDefaults] setBool:NO forKey:@"firstStamp"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  if (![[NSUserDefaults standardUserDefaults] boolForKey:@"hasStamped"] &&
      [AccountManager sharedManager].currentUser.numStamps &&
      [AccountManager sharedManager].currentUser.numStamps.intValue == 0) { 
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
                       animations:^{tooltipImageView_.alpha = 1.0;}
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

- (void)overlayWasTapped:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [UIView animateWithDuration:0.3 animations:^{
    recognizer.view.alpha = 0.0;
  } completion:^(BOOL finished) {
    [recognizer.view removeFromSuperview];
  }];
}

- (void)stampWasCreated:(NSNotification*)notification {
  if (self.tabBar.selectedItem != mustDoTabBarItem_) {
    self.tabBar.selectedItem = stampsTabBarItem_;
    [self tabBar:self.tabBar didSelectItem:stampsTabBarItem_];
  }
}

- (void)newsCountChanged:(NSNotification*)notification {
  NSNumber* newItemCount = notification.object;
  if (self.tabBar.selectedItem != activityTabBarItem_)
    activityTabBarItem_.badgeValue = [newItemCount stringValue];
}

- (void)reloadPanes:(NSNotification*)notification {
  for (STTableViewController* viewController in self.viewControllers) {
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
  [((InboxViewController*)[self.viewControllers objectAtIndex:0]) reloadData];
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
    [[UIApplication sharedApplication] setApplicationIconBadgeNumber:1];
    [[UIApplication sharedApplication] setApplicationIconBadgeNumber:0];
  } else if (item == mustDoTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:2];
    self.navigationItem.title = @"To-Do";
  } else if (item == peopleTabBarItem_) {
    newViewController = [viewControllers_ objectAtIndex:3];
    self.navigationItem.title = @"People";
  }
  [(STNavigationBar*)self.navigationController.navigationBar setListButtonShown:NO];  
  [self.navigationController.navigationBar setNeedsDisplay];

  if (!newViewController || newViewController == self.selectedViewController)
    return;

  // TODO(andybons): iOS 5 child view controllers.
  [self.selectedViewController viewWillDisappear:NO];
  [self.selectedViewController.view removeFromSuperview];
  [self.selectedViewController viewDidDisappear:NO];
  [newViewController viewWillAppear:NO];
  [self.view insertSubview:newViewController.view atIndex:0];
  [self ensureCorrectHeightOfViewControllers];
  [newViewController viewDidAppear:NO];
  self.selectedViewController = newViewController;
  selectedViewControllerIndex_ = [tabBarItems_ indexOfObject:item];
}

@end