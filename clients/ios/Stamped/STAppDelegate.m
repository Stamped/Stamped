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
#import "STActionManager.h"
#import "STCalloutView.h"
#import "STConfirmationView.h"
#import "STUniversalNewsController.h"

#import "FindFriendsViewController.h"
#import "STUserViewController.h"
#import "STPlayer.h"
#import "STDebug.h"

//static NSString* const kLocalDataBaseURL = @"http://localhost:18000/v0";
//#if defined (DEV_BUILD)
//static NSString* const kDataBaseURL = @"https://dev.stamped.com/v0";
//#else
//static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
//#endif
//static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface STAppDelegate ()

- (void)addConfigurations;

@end

@implementation STAppDelegate

@synthesize window = _window;
@synthesize menuController = _menuController;
@synthesize grid = grid_;

- (void)dealloc {
    //Not important
    [super dealloc];
}

- (void)application:(UIApplication *)application didChangeStatusBarFrame:(CGRect)oldStatusBarFrame {
    
}

- (void)application:(UIApplication *)application didChangeStatusBarOrientation:(UIInterfaceOrientation)oldStatusBarOrientation {
}

- (UIImage*)stampImageWithPrimaryColor:(NSString*)primaryColor andSecondaryColor:(NSString*)secondaryColor {
    return [Util gradientImage:[UIImage imageNamed:@"largestampedlogo"] withPrimaryColor:primaryColor secondary:secondaryColor];
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    //#if defined (CONFIGURATION_Beta)
    //  [[BWHockeyManager sharedHockeyManager] setAppIdentifier:@"eed3b68dbf577e8e1a9ce46a83577ead"];
    //[[BWHockeyManager sharedHockeyManager] setDelegate:self];
    //#endif
    
#if defined (CONFIGURATION_Beta)
#warning QuincyKit Beta (Ad Hoc) is configured for this build
//    NSString* key;
//    key = @"bdc37071b6cd3a6cee047008f0d1a792"; //internal
//    key = @"eed3b68dbf577e8e1a9ce46a83577ead"; //beta
//    [[BWQuincyManager sharedQuincyManager] setAppIdentifier:key];
#endif
    
    
#if defined (CONFIGURATION_Release)
#warning QuincyKit Distribution is configured for this build
    //    [[BWQuincyManager sharedQuincyManager] setAppIdentifier:@"062d51bb10ae8a23648feb2bfea4bd1d"];
#endif
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didLogIn:) name:STStampedAPILoginNotification object:nil];
    RKLogConfigureByName("RestKit*", RKLogLevelError);
    RKLogSetAppLoggingLevel(RKLogLevelError);
    [self addConfigurations];
    [self customizeAppearance];
    
    self.window = [[[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]] autorelease];
    self.window.backgroundColor = [UIColor whiteColor];
    STLeftMenuViewController *leftController = [[[STLeftMenuViewController alloc] init] autorelease];
    STRightMenuViewController *rightController = [[[STRightMenuViewController alloc] init] autorelease];
    
    STMenuController* menuController = [[[STMenuController alloc] init] autorelease];
    menuController.leftViewController = leftController;
    menuController.rightViewController = rightController;
    self.menuController = menuController;
    self.menuController.pan.enabled = NO;
    [self.window setRootViewController:menuController];
    [self.window makeKeyAndVisible];
    grid_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"column-grid"]];
    grid_.hidden = YES;
    [self.window addSubview:grid_];
    NSString* versionMessage = [NSString stringWithFormat:@"Version:%@",[Util versionString]];
    STLog(versionMessage);
    [Util executeAsync:^{
        [Util removeOldCacheDirectories];
    }];
    
    UIImageView *imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"launchscreen"]] autorelease];
    imageView.layer.shadowRadius = 8;
    imageView.layer.shadowOffset = CGSizeMake(0, 4);
    imageView.layer.shadowOpacity = .3;
    imageView.layer.shadowColor = [UIColor blackColor].CGColor;
    [Util reframeView:imageView withDeltas:CGRectMake(0, 20, 0, 0)];
    UIImageView* stampView = [[[UIImageView alloc] initWithImage:[self stampImageWithPrimaryColor:@"004AB3" andSecondaryColor:@"0055CC"]] autorelease];
    stampView.frame = [Util centeredAndBounded:stampView.image.size inFrame:CGRectMake(0, -20, imageView.frame.size.width, imageView.frame.size.height)];
    [imageView addSubview:stampView];
    [self.window addSubview:imageView];
    
    
    [[STRestKitLoader sharedInstance] authenticateWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {    
        if ([STStampedAPI sharedInstance].currentUser) {
            [self didLogIn:nil];
        }
        BOOL openedWithAPNS = [launchOptions objectForKey:UIApplicationLaunchOptionsRemoteNotificationKey] != nil;
        UIViewController* firstController;
        if (openedWithAPNS && LOGGED_IN) {
            firstController = [[[STUniversalNewsController alloc] init] autorelease];
        }
        else {
            firstController =  [[[STInboxViewController alloc] init] autorelease];
        }
        [Util addHomeButtonToController:firstController withBadge:!openedWithAPNS];
        STRootViewController* navController = [[STRootViewController alloc] initWithRootViewController:firstController];
        [self.menuController setRootController:navController animated:NO];
        
        if (LOGGED_IN) {
            [[STUnreadActivity sharedInstance] update];
            id<STUserDetail> currentUser = [STStampedAPI sharedInstance].currentUser;
            if (currentUser) {
                UIImageView* stampView2 = [[[UIImageView alloc] initWithImage:[self stampImageWithPrimaryColor:currentUser.primaryColor andSecondaryColor:currentUser.secondaryColor]] autorelease];
                stampView2.frame = stampView.frame;
                stampView2.alpha = 0;
                [imageView addSubview:stampView2];
                [UIView animateWithDuration:.3 delay:0 options:UIViewAnimationCurveEaseInOut animations:^{
                    stampView2.alpha = 1;
                    stampView.alpha = 0;
                } completion:^(BOOL finished) {
                    
                }];
            }
        }
        else {
            [self.menuController showWelcome:NO];
        }
        [UIView animateWithDuration:.7 delay:1 options:UIViewAnimationCurveEaseInOut animations:^{
            imageView.frame = CGRectOffset(imageView.frame, 0, -CGRectGetMaxY(imageView.frame));
        } completion:^(BOOL finished) {
            [imageView removeFromSuperview];
        }];
    }];
    
    return YES;
}

- (void)didLogIn:(id)notImportant {
    [[UIApplication sharedApplication] registerForRemoteNotificationTypes:(UIRemoteNotificationTypeAlert | 
                                                                           UIRemoteNotificationTypeBadge | 
                                                                           UIRemoteNotificationTypeSound)];
}

- (void)application:(UIApplication *)application didFailToRegisterForRemoteNotificationsWithError:(NSError *)error {
    NSString* msg = [NSString stringWithFormat:@"APNS registration failed: %@", error];
    STLog(msg);
}

- (void)application:(UIApplication *)application didReceiveLocalNotification:(UILocalNotification *)notification {
}

/*
 Apple was actually helpful and clear!!!
 
 From Apple's "Local and Push Notification Programming Guide":
 iOS Note: In iOS, you can determine whether an application is launched as a result of the user tapping the action button
 or whether the notification was delivered to the already-running application by examining the application state. In the delegate’s
 implementation of the application:didReceiveRemoteNotification: or application:didReceiveLocalNotification: method, get the value
 of the applicationState property and evaluate it. If the value is UIApplicationStateInactive, the user tapped the action button;
 if the value is UIApplicationStateActive, the application was frontmost when it received the notification.
 */

- (void)application:(UIApplication *)application didReceiveRemoteNotification:(NSDictionary *)userInfo {
    if (!LOGGED_IN) return;
    BOOL shouldGoToNews = application.applicationState == UIApplicationStateInactive;
    if (shouldGoToNews) {
        STMenuController* menuController = self.menuController;
        while (menuController.presentedViewController) {
            [menuController dismissModalViewControllerAnimated:NO];
        }
        UIViewController* controller = [[[STUniversalNewsController alloc] init] autorelease];
        [Util addHomeButtonToController:controller withBadge:NO];
        STRootViewController* rootViewController = [[[STRootViewController alloc] initWithRootViewController:controller] autorelease];
        [menuController setRootController:rootViewController animated:NO];
        [(STLeftMenuViewController*)menuController.leftViewController clearSelection];
        //TODO go staight to news
        //        [[STUnreadActivity sharedInstance] update];
    }
    else {
        [[STUnreadActivity sharedInstance] update];
    }
}

- (void)application:(UIApplication *)application didRegisterForRemoteNotificationsWithDeviceToken:(NSData *)devToken {
    if (LOGGED_IN) {
        NSString* deviceToken = [NSString stringWithFormat:@"%@", devToken];
        deviceToken = [deviceToken stringByTrimmingCharactersInSet:[NSCharacterSet characterSetWithCharactersInString:@"<>"]];
        deviceToken = [deviceToken stringByReplacingOccurrencesOfString:@" " withString:@""];
        [[STStampedAPI sharedInstance] registerAPNSToken:deviceToken andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
            NSLog(@"Registered %@", deviceToken); 
        }];
    }
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {
    if ([[url host] isEqualToString:@"twitter"] && [url query].length > 0) {
        [[STTwitter sharedInstance] handleOpenURL:url];
	}  
    else if ([[url description] hasPrefix:@"fb297022226980395"]) {
        [[[STFacebook sharedInstance] facebook] handleOpenURL:url];
	}
    else if ([[url scheme] isEqualToString:@"stamped"]) {
        NSString* message = [url.resourceSpecifier stringByReplacingCharactersInRange:NSMakeRange(0, 2) withString:@""];
        NSString* netflixPrefix = @"netflix/";
        if ([message hasPrefix:netflixPrefix]) {
            NSString* netflixMessage = [message stringByReplacingCharactersInRange:NSMakeRange(0, netflixPrefix.length) withString:@""];
            NSString* subtitle = nil;
            NSString* title = @"";
            UIImage* icon = [UIImage imageNamed:@"3rd_icon_netflix"];
            if ([netflixMessage isEqualToString:@"link/success"]) {
                title = @"Connected to Netflix";
            }
            else if ([netflixMessage isEqualToString:@"link/fail"]) {
                title = @"Problem connecting to Netflix";
            }
            else if ([netflixMessage isEqualToString:@"add/success"]) {
                title = @"Added to Instant Queue";
            }
            else if ([netflixMessage isEqualToString:@"add/fail"]) {
                title = @"Problem connecting to Netflix";
            }
            STConfirmationView* view = [[[STConfirmationView alloc] initWithTille:title subtitle:subtitle andIconImage:icon] autorelease];
            view.frame = [Util centeredAndBounded:view.frame.size inFrame:[Util fullscreenFrameAdjustedForStatusBar]];
            [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor colorWithWhite:0 alpha:.1]];
        }
    }
    
    return YES;
}

- (void)application:(UIApplication *)application willChangeStatusBarFrame:(CGRect)newStatusBarFrame {
    
}

- (void)application:(UIApplication *)application willChangeStatusBarOrientation:(UIInterfaceOrientation)newStatusBarOrientation duration:(NSTimeInterval)duration {
    
}

- (void)applicationDidBecomeActive:(UIApplication *)application {
    [STStampedAPI sharedInstance].currentUserLocation = nil;
    [[STUnreadActivity sharedInstance] update];
    if ([STFacebook sharedInstance].connected) {
        [[STFacebook sharedInstance].facebook extendAccessToken];
    }
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
    [STStampedAPI sharedInstance].currentUserLocation = nil;
}

- (void)applicationDidReceiveMemoryWarning:(UIApplication *)application {
    [[STImageCache sharedInstance] fastPurge];
    [[STStampedAPI sharedInstance] fastPurge];
    STLog(@"memory warning");
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
    
    [STConfiguration addColor:[UIColor colorWithRed:1 green:1 blue:1 alpha:.8] forKey:@"UIColor.stampedLightGradientStart" inSection:@"UIColor"];
    [STConfiguration addColor:[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6] forKey:@"UIColor.stampedLightGradientEnd" inSection:@"UIColor"];
    
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
    
    //Actions
    [STActionManager setupConfigurations];
    
    [STCalloutView setupConfigurations];
    
    [STPlayer setupConfigurations];
}

@end
