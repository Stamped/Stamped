//
//  STAppDelegate.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAppDelegate.h"
#import "STRootViewController.h"
#import "BWQuincyManager.h"
#import <RestKit/RestKit.h>
#import "STNavigationBar.h"
#import "STDebug.h"
#import "Util.h"
#import "STRootScrollView.h"
#import "STLeftMenuViewController.h"
#import "STRightMenuViewController.h"
#import "STConfiguration.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STInboxViewController.h"
#import "STIWantToViewController.h"
#import "STUniversalNewsController.h"
#import "STTodoViewController.h"
#import "STDebugViewController.h"
#import "STSettingsViewController.h"
#import "STStampCell.h"
#import "STImageCache.h"
#import "STStampedAPI.h"
#import "DDMenuController.h"
#import "STMenuController.h"
#import "STIWantToViewController.h"
#import "STSharedCaches.h"
#import "STTwitter.h"
#import "STFacebook.h"
#import "STRestKitLoader.h"
#import "STUnreadActivity.h"

#import "STCreateStampViewController.h"
#import "FindFriendsViewController.h"
#import "STUserViewController.h"

static NSString* const kLocalDataBaseURL = @"http://localhost:18000/v0";
#if defined (DEV_BUILD)
static NSString* const kDataBaseURL = @"https://dev.stamped.com/v0";
#else
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
#endif
static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface STAppDelegate ()

- (void)addConfigurations;

@end

@implementation STAppDelegate

@synthesize window = _window;
@synthesize menuController = _menuController;
@synthesize navigationController = _navigationController;
@synthesize grid = grid_;

- (void)dealloc {
    [_window release];
    [_navigationController release];
    [grid_ release];
    [super dealloc];
}

- (void)application:(UIApplication *)application didChangeStatusBarFrame:(CGRect)oldStatusBarFrame {
    
}

- (void)application:(UIApplication *)application didChangeStatusBarOrientation:(UIInterfaceOrientation)oldStatusBarOrientation {
}

- (void)application:(UIApplication *)application didFailToRegisterForRemoteNotificationsWithError:(NSError *)error {
    
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    //#if defined (CONFIGURATION_Beta)
    //  [[BWHockeyManager sharedHockeyManager] setAppIdentifier:@"eed3b68dbf577e8e1a9ce46a83577ead"];
    //[[BWHockeyManager sharedHockeyManager] setDelegate:self];
    //#endif
    
#if defined (CONFIGURATION_Beta)
#warning QuincyKit Beta (Ad Hoc) is configured for this build
    [[BWQuincyManager sharedQuincyManager] setAppIdentifier:@"eed3b68dbf577e8e1a9ce46a83577ead"];
#endif
    
    
#if defined (CONFIGURATION_Release)
#warning QuincyKit Distribution is configured for this build
    [[BWQuincyManager sharedQuincyManager] setAppIdentifier:@"062d51bb10ae8a23648feb2bfea4bd1d"];
#endif
    RKLogConfigureByName("RestKit*", RKLogLevelError);
    RKLogSetAppLoggingLevel(RKLogLevelError);
    [self addConfigurations];
    [self customizeAppearance];
    
    CGSize textSize = [Util sizeForString:[Util attributedStringForString:@"This is a test\nasd basdf\na" 
                                                                     font:[UIFont stampedFontWithSize:10] 
                                                                    color:[UIColor blackColor] 
                                                               lineHeight:16]
                                 thatFits:CGSizeMake(100, CGFLOAT_MAX)];
    NSLog(@"%f,%f",textSize.width, textSize.height);
    
    self.window = [[[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]] autorelease];
    self.window.backgroundColor = [UIColor whiteColor];
    [[STRestKitLoader sharedInstance] authenticate];
    NSLog(@"USer:%@", [STStampedAPI sharedInstance].currentUser);
    STInboxViewController *inboxController = [[STInboxViewController alloc] init];
    STLeftMenuViewController *leftController = [[STLeftMenuViewController alloc] init];
    STRightMenuViewController *rightController = [[STRightMenuViewController alloc] init];
    
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:inboxController];
    _navigationController = [navController retain];
    STMenuController *menuController = [[STMenuController alloc] initWithRootViewController:navController];
    menuController.leftViewController = leftController;
    menuController.rightViewController = rightController;
    self.menuController = menuController;
    
    [Util addHomeButtonToController:inboxController withBadge:YES];
    
    [inboxController release];
    [leftController release];
    [rightController release];
    [menuController release];
    [navController release];
    
    [self.window setRootViewController:menuController];
    [self.window makeKeyAndVisible];
    
    grid_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"column-grid"]];
    grid_.hidden = YES;
    [self.window addSubview:grid_];
    STLog(@"Finished Loading application");
    [Util executeAsync:^{
        [Util removeOldCacheDirectories];
    }];
    
    [[STUnreadActivity sharedInstance] update];
    
    return YES;
}

- (void)application:(UIApplication *)application didReceiveLocalNotification:(UILocalNotification *)notification {
    
}

- (void)application:(UIApplication *)application didReceiveRemoteNotification:(NSDictionary *)userInfo {
    
}

- (void)application:(UIApplication *)application didRegisterForRemoteNotificationsWithDeviceToken:(NSData *)deviceToken {
    
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {
    
    if ([[url host] isEqualToString:@"twitter"] && [url query].length > 0) {
        [[STTwitter sharedInstance] handleOpenURL:url];
	}  else if ([[url description] hasPrefix:@"fb297022226980395"]) {
        [[[STFacebook sharedInstance] facebook] handleOpenURL:url];
	}
    
    return YES;
}

- (void)application:(UIApplication *)application willChangeStatusBarFrame:(CGRect)newStatusBarFrame {
    
}

- (void)application:(UIApplication *)application willChangeStatusBarOrientation:(UIInterfaceOrientation)newStatusBarOrientation duration:(NSTimeInterval)duration {
    
}

- (void)applicationDidBecomeActive:(UIApplication *)application {
    
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
    /* NSLog(@"Going to background");
     [[STSharedCaches cacheForInboxScope:STStampedAPIScopeFriends] saveWithAccelerator:nil andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
     NSLog(@"Saved"); 
     }];
     */
}

- (void)applicationDidFinishLaunching:(UIApplication *)application {
    
}

- (void)applicationDidReceiveMemoryWarning:(UIApplication *)application {
    [[STImageCache sharedInstance] fastPurge];
    [[STStampedAPI sharedInstance] fastPurge];
}

- (void)applicationProtectedDataDidBecomeAvailable:(UIApplication *)application {
    
}

- (void)applicationProtectedDataWillBecomeUnavailable:(UIApplication *)application {
}

- (void)applicationSignificantTimeChange:(UIApplication *)application {
    
}

- (void)applicationWillEnterForeground:(UIApplication *)application {
    
}

- (void)applicationWillResignActive:(UIApplication *)application {
    
}

- (void)applicationWillTerminate:(UIApplication *)application {
    
}


- (void)customizeAppearance {
    return;
    if (![UIBarButtonItem conformsToProtocol:@protocol(UIAppearance)])
        return;
    
    UIImage* buttonImage = [[UIImage imageNamed:@"default_nav_button_bg"] resizableImageWithCapInsets:UIEdgeInsetsMake(0, 5, 0, 5)];
    [[UIBarButtonItem appearanceWhenContainedIn:[STNavigationBar class], nil] setBackgroundImage:buttonImage
                                                                                        forState:UIControlStateNormal 
                                                                                      barMetrics:UIBarMetricsDefault];
    
    UIImage* backButtonImage = [[UIImage imageNamed:@"default_back_button_bg"]
                                resizableImageWithCapInsets:UIEdgeInsetsMake(0, 13, 0, 5)];
    
    
    [[UIBarButtonItem appearanceWhenContainedIn:[STNavigationBar class], nil] setBackButtonBackgroundImage:backButtonImage
                                                                                                  forState:UIControlStateNormal
                                                                                                barMetrics:UIBarMetricsDefault];
    [[UIBarButtonItem appearanceWhenContainedIn:[STNavigationBar class], nil] setBackButtonTitlePositionAdjustment:UIOffsetMake(1, 0)
                                                                                                     forBarMetrics:UIBarMetricsDefault];
    [[UIBarButtonItem appearanceWhenContainedIn:[STNavigationBar class], nil] setTitleTextAttributes:
     [NSDictionary dictionaryWithObjectsAndKeys:
      [UIColor colorWithWhite:0.7 alpha:1.0], UITextAttributeTextColor, 
      [UIColor whiteColor], UITextAttributeTextShadowColor, 
      [NSValue valueWithUIOffset:UIOffsetMake(0, 1)], UITextAttributeTextShadowOffset, nil] 
                                                                                            forState:UIControlStateNormal];
    [[UIBarButtonItem appearanceWhenContainedIn:[STNavigationBar class], nil] setTitleTextAttributes:
     [NSDictionary dictionaryWithObjectsAndKeys:
      [UIColor whiteColor], UITextAttributeTextColor,
      [NSValue valueWithUIOffset:UIOffsetMake(0, 0)], UITextAttributeTextShadowOffset, nil] 
                                                                                            forState:UIControlStateHighlighted];
    
    [[UITabBar appearance] setSelectionIndicatorImage:[UIImage imageNamed:@"clear_image"]];
    
    
    UIImage* segmentSelected = [[UIImage imageNamed:@"segmentedControl_sel"] resizableImageWithCapInsets:UIEdgeInsetsMake(4, 5, 5, 5)];
    UIImage* segmentUnselected = [[UIImage imageNamed:@"segmentedControl_uns"] resizableImageWithCapInsets:UIEdgeInsetsMake(4, 5, 5, 5)];
    UIImage* segmentDivUnselectedUnselected = [UIImage imageNamed:@"segmentedControl_div_uns_uns"];
    UIImage* segmentDivSelectedUnselected = [UIImage imageNamed:@"segmentedControl_div_sel_uns"];
    UIImage* segmentDivUnselectedSelected = [UIImage imageNamed:@"segmentedControl_div_uns_sel"];
    
    [[UISegmentedControl appearance] setBackgroundImage:segmentUnselected forState:UIControlStateNormal barMetrics:UIBarMetricsDefault];
    [[UISegmentedControl appearance] setBackgroundImage:segmentSelected forState:UIControlStateSelected barMetrics:UIBarMetricsDefault];
    [[UISegmentedControl appearance] setDividerImage:segmentDivUnselectedUnselected
                                 forLeftSegmentState:UIControlStateNormal
                                   rightSegmentState:UIControlStateNormal
                                          barMetrics:UIBarMetricsDefault];
    [[UISegmentedControl appearance] setDividerImage:segmentDivSelectedUnselected
                                 forLeftSegmentState:UIControlStateSelected
                                   rightSegmentState:UIControlStateNormal
                                          barMetrics:UIBarMetricsDefault];
    [[UISegmentedControl appearance] setDividerImage:segmentDivUnselectedSelected
                                 forLeftSegmentState:UIControlStateNormal
                                   rightSegmentState:UIControlStateSelected
                                          barMetrics:UIBarMetricsDefault];
}

- (void)addConfigurations {
    
    [STLeftMenuViewController setupConfigurations];
    //Root Menu
    NSDictionary* inboxChoices = [NSDictionary dictionaryWithObjectsAndKeys:
                                  [STInboxViewController class], @"New Inbox",
                                  nil];
    [STConfiguration addChoices:inboxChoices originalKey:@"New Inbox" forKey:@"Root.inbox"];
    [STConfiguration addValue:[STIWantToViewController class] forKey:@"Root.iWantTo"];
    [STConfiguration addValue:[STUniversalNewsController class] forKey:@"Root.news"];
    [STConfiguration addValue:[FindFriendsViewController class] forKey:@"Root.findFriends"];
    [STConfiguration addValue:[STUserViewController class] forKey:@"Root.user"];
    [STConfiguration addValue:[STTodoViewController class] forKey:@"Root.todo"];
    [STConfiguration addValue:[STDebugViewController class] forKey:@"Root.debug"];
    [STConfiguration addValue:[STSettingsViewController class] forKey:@"Root.settings"];
    NSDictionary* choices = [NSDictionary dictionaryWithObjectsAndKeys:
                             @"created", @"Created",
                             @"modified", @"Modified",
                             @"stamped", @"Stamped",
                             nil];
    [STConfiguration addChoices:choices originalKey:@"Stamped" forKey:@"Root.inboxSort"];
    
    //UIColor
    
    [STConfiguration addFont:[UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:35] forKey:@"UIFont.stampedTitleFont" inSection:@"UIFont"];
    [STConfiguration addFont:[UIFont fontWithName:@"TitlingGothicFBComp-Light" size:35] forKey:@"UIFont.stampedTitleLightFont" inSection:@"UIFont"];
    
    CGFloat fontSize = 12;
    [STConfiguration addFont:[UIFont fontWithName:@"HelveticaNeue" size:fontSize] forKey:@"UIFont.stampedFont" inSection:@"UIFont"];
    [STConfiguration addFont:[UIFont fontWithName:@"HelveticaNeue-Bold" size:fontSize] forKey:@"UIFont.stampedBoldFont" inSection:@"UIFont"];
    [STConfiguration addFont:[UIFont fontWithName:@"HelveticaNeue" size:fontSize] forKey:@"UIFont.stampedSubtitleFont" inSection:@"UIFont"];
    
    //UIColor
    
    [STConfiguration addColor:[UIColor colorWithRed:.15 green:.15 blue:0.15 alpha:1.0] forKey:@"UIColor.stampedBlackColor" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.35 green:.35 blue:0.35 alpha:1.0] forKey:@"UIColor.stampedDarkGrayColor" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.6 green:.6 blue:0.6 alpha:1.0] forKey:@"UIColor.stampedGrayColor" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.75 green:.75 blue:0.75 alpha:1.0] forKey:@"UIColor.stampedLightGrayColor" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.2 green:.2 blue:.7 alpha:1] forKey:@"UIColor.stampedLinkColor" inSection:@"UIColor"];
    
    [STConfiguration addColor:[UIColor colorWithRed:.99 green:.99 blue:.99 alpha:1] forKey:@"UIColor.stampedLightGradientStart" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.90 green:.90 blue:.90 alpha:1] forKey:@"UIColor.stampedLightGradientEnd" inSection:@"UIColor"];
    
    [STConfiguration addColor:[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:1] forKey:@"UIColor.stampedGradientStart" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.85 green:.85 blue:.85 alpha:1] forKey:@"UIColor.stampedGradientEnd" inSection:@"UIColor"];
    
    [STConfiguration addColor:[UIColor colorWithRed:.85 green:.85 blue:.85 alpha:1] forKey:@"UIColor.stampedDarkGradientStart" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.7 green:.7 blue:.7 alpha:1] forKey:@"UIColor.stampedDarkGradientEnd" inSection:@"UIColor"];
    
    CGFloat rgbTop[3];
    CGFloat rgbBottom[3];
    [Util splitHexString:@"498ff2" toRGB:rgbTop];
    [Util splitHexString:@"0b61d9" toRGB:rgbBottom];
    [STConfiguration addColor:[UIColor colorWithRed:rgbTop[0] green:rgbTop[1] blue:rgbTop[2] alpha:1] forKey:@"UIColor.stampedBlueGradientStart"];
    [STConfiguration addColor:[UIColor colorWithRed:rgbBottom[0] green:rgbBottom[1] blue:rgbBottom[2] alpha:1] forKey:@"UIColor.stampedBlueGradientEnd"];
    
    [STConfiguration addChoices:[NSDictionary dictionaryWithObjectsAndKeys:
                                 [UIColor stampedBlueGradient], @"Blue",
                                 [UIColor stampedDarkGradient], @"Dark Gray",
                                 [UIColor stampedGradient], @"Gray",
                                 nil]
                    originalKey:@"Blue"
                         forKey:@"UIColor.buttonGradient"];
    // Comments
    [STConfiguration addFont:[UIFont stampedBoldFontWithSize:12] forKey:@"Comments.font"];
    
    //I Want to
    [STIWantToViewController setupConfigurations];
    
    //Stamp Cell
    //[STStampCell setupConfigurations];
    //[STStampCell setupConfigurations];
    
    //Create Stamp
    [STCreateStampViewController setupConfigurations];
}

@end
