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
#import "STRootMenuView.h"
#import "STLegacyInboxViewController.h"
#import "OAuthToken.h"
#import "DetailedEntity.h"
#import "User.h"
#import "Entity.h"
#import "Comment.h"
#import "Favorite.h"
#import "Event.h"
#import "AccountManager.h"
#import "SearchResult.h"
#import "STNavigationBar.h"
#import "STDebug.h"
#import "Util.h"
#import "STRootScrollView.h"
#import "ECSlidingViewController.h"
#import "STLeftMenuViewController.h"
#import "STRightMenuViewController.h"
#import "STConfiguration.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STLegacyInboxViewController.h"
#import "STInboxViewController.h"
#import "STIWantToViewController.h"
#import "STUniversalNewsController.h"
#import "STTodoViewController.h"
#import "STDebugViewController.h"
#import "SettingsViewController.h"
#import "STStampCell.h"
#import "STImageCache.h"
#import "STStampedAPI.h"
#import "STCreateStampViewController.h"

static NSString* const kLocalDataBaseURL = @"http://localhost:18000/v0";
#if defined (DEV_BUILD)
static NSString* const kDataBaseURL = @"https://dev.stamped.com/v0";
#else
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
#endif
static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface STAppDelegate ()

- (void)performRestKitMappings;
- (void)addConfigurations;

@end

@implementation STAppDelegate

@synthesize window = _window;
@synthesize navigationController = _navigationController;
@synthesize grid = grid_;

- (void)dealloc
{
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
#if defined (CONFIGURATION_Beta)
#warning QuincyKit Beta (Ad Hoc) is configured for this build
  [[BWQuincyManager sharedQuincyManager] setAppIdentifier:@"3999903c72892bb98e58f843990bba66"];
#endif
  
#if defined (CONFIGURATION_Release)
#warning QuincyKit Distribution is configured for this build
  [[BWQuincyManager sharedQuincyManager] setAppIdentifier:@"062d51bb10ae8a23648feb2bfea4bd1d"];
#endif
  RKLogConfigureByName("RestKit*", RKLogLevelError);
  RKLogSetAppLoggingLevel(RKLogLevelError);
  [self addConfigurations];
  [self customizeAppearance];
  [self performRestKitMappings];
  self.window = [[[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]] autorelease];
  // Override point for customization after application launch.
  self.window.backgroundColor = [UIColor whiteColor];
  _navigationController = [[STRootViewController alloc] init];
  [self.window setRootViewController:_navigationController];
  ECSlidingViewController* slider = [ECSlidingViewController sharedInstance];
  NSLog(@"Slider:%f,%f vs %f",slider.view.frame.size.height, slider.view.frame.origin.y, self.window.frame.size.height);
  slider.topViewController = _navigationController;
  [self.window setRootViewController:slider];
  [self.window makeKeyAndVisible];
  slider.underLeftViewController = [[[STLeftMenuViewController alloc] init] autorelease];
  slider.underRightViewController = [[[STRightMenuViewController alloc] init] autorelease];
  [[AccountManager sharedManager] authenticate];
  [_navigationController pushViewController:[[[STInboxViewController alloc] init] autorelease] animated:NO];
  grid_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"column-grid"]];
  grid_.hidden = YES;
  [self.window addSubview:grid_];
  STLog(@"Finished Loading application");
  return YES;
}

- (void)application:(UIApplication *)application didReceiveLocalNotification:(UILocalNotification *)notification {
  
}

- (void)application:(UIApplication *)application didReceiveRemoteNotification:(NSDictionary *)userInfo {
  
}

- (void)application:(UIApplication *)application didRegisterForRemoteNotificationsWithDeviceToken:(NSData *)deviceToken {
  
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {
  return NO;
}

- (void)application:(UIApplication *)application willChangeStatusBarFrame:(CGRect)newStatusBarFrame {
  
}

- (void)application:(UIApplication *)application willChangeStatusBarOrientation:(UIInterfaceOrientation)newStatusBarOrientation duration:(NSTimeInterval)duration {
  
}

- (void)applicationDidBecomeActive:(UIApplication *)application {
  
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
  
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


- (void)performRestKitMappings {
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDataBaseURL];
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  [RKClient sharedClient].requestQueue.delegate = [AccountManager sharedManager];
  [RKClient sharedClient].requestQueue.requestTimeout = 30;
  [RKClient sharedClient].requestQueue.concurrentRequestsLimit = 3;
  
  RKManagedObjectMapping* userMapping = [RKManagedObjectMapping mappingForClass:[User class]];
  [userMapping mapKeyPathsToAttributes:@"user_id", @"userID",
   @"name", @"name",
   @"color_primary", @"primaryColor",
   @"color_secondary", @"secondaryColor",
   @"screen_name", @"screenName",
   @"num_credits", @"numCredits",
   @"num_followers", @"numFollowers",
   @"num_friends", @"numFriends",
   @"num_stamps", @"numStamps",
   @"num_stamps_left", @"numStampsLeft",
   @"image_url", @"imageURL", nil];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapAttributes:@"bio", @"website", @"location", @"identifier", nil];
  
  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  entityMapping.primaryKeyAttribute = @"entityID";
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID", nil];
  [entityMapping mapAttributes:@"category", @"subtitle", @"title", @"coordinates", @"subcategory", nil];
  
  RKManagedObjectMapping* detailedEntityMapping = [RKManagedObjectMapping mappingForClass:[DetailedEntity class]];
  detailedEntityMapping.primaryKeyAttribute = @"entityID";
  [detailedEntityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID",
   @"opentable_url", @"openTableURL",
   @"itunes_short_url", @"itunesShortURL",
   @"itunes_url", @"itunesURL",
   @"artist_name", @"artist",
   @"release_date", @"releaseDate",
   @"amazon_url", @"amazonURL",
   @"in_theaters", @"inTheaters",
   @"fandango_url", @"fandangoURL", nil];
  [detailedEntityMapping mapAttributes:@"address", @"category", @"subtitle",
   @"title", @"coordinates", @"phone", @"subcategory",
   @"street", @"substreet", @"city", @"state", @"zipcode",
   @"neighborhood", @"desc", @"genre", @"label", @"length",
   @"author", @"cast", @"director", @"year", @"hours", @"cuisine",
   @"price", @"website", @"rating", @"isbn", @"format", 
   @"publisher", @"language", @"albums", @"songs",
   @"image", nil];
  
  RKManagedObjectMapping* commentMapping = [RKManagedObjectMapping mappingForClass:[Comment class]];
  [commentMapping mapAttributes:@"blurb", @"created", nil];
  [commentMapping mapKeyPathsToAttributes:@"comment_id", @"commentID",
   @"restamp_id", @"restampID",
   @"stamp_id", @"stampID", nil];
  commentMapping.primaryKeyAttribute = @"commentID";
  [commentMapping mapRelationship:@"user" withMapping:userMapping];
  
  RKManagedObjectMapping* stampMapping = [RKManagedObjectMapping mappingForClass:[Stamp class]];
  [stampMapping mapKeyPathsToAttributes:@"stamp_id", @"stampID",
   @"created", @"created",
   @"num_comments", @"numComments",
   @"num_likes", @"numLikes",
   @"is_liked", @"isLiked",
   @"is_fav", @"isFavorited",
   @"image_dimensions", @"imageDimensions",
   @"image_url", @"imageURL",
   @"url", @"URL", nil];
  stampMapping.primaryKeyAttribute = @"stampID";
  [stampMapping mapAttributes:@"blurb", @"modified", @"deleted", @"via", nil];
  [stampMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [stampMapping mapRelationship:@"user" withMapping:userMapping];
  [stampMapping mapKeyPath:@"comment_preview" toRelationship:@"comments" withMapping:commentMapping];
  [stampMapping mapKeyPath:@"credit" toRelationship:@"credits" withMapping:userMapping];
  
  [userMapping mapRelationship:@"credits" withMapping:stampMapping];
  
  RKManagedObjectMapping* eventMapping = [RKManagedObjectMapping mappingForClass:[Event class]];
  [eventMapping mapAttributes:@"created", @"genre", @"subject", @"blurb", @"benefit", @"icon", @"image", nil];
  [eventMapping mapKeyPath:@"activity_id" toAttribute:@"eventID"];
  [eventMapping mapKeyPath:@"subject_objects" toAttribute:@"subjectObjects"];
  [eventMapping mapKeyPath:@"blurb_objects" toAttribute:@"blurbObjects"];
  [eventMapping mapKeyPath:@"linked_url" toAttribute:@"urlObject"];
  eventMapping.primaryKeyAttribute = @"eventID";
  [eventMapping mapKeyPath:@"linked_entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [eventMapping mapKeyPath:@"linked_stamp" toRelationship:@"stamp" withMapping:stampMapping];
  [eventMapping mapRelationship:@"user" withMapping:userMapping];
  
  RKManagedObjectMapping* favoriteMapping = [RKManagedObjectMapping mappingForClass:[Favorite class]];
  [favoriteMapping mapAttributes:@"complete", @"created", nil];
  [favoriteMapping mapKeyPathsToAttributes:@"favorite_id", @"favoriteID", @"user_id", @"userID", nil];
  favoriteMapping.primaryKeyAttribute = @"favoriteID";
  [favoriteMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [favoriteMapping mapRelationship:@"stamp" withMapping:stampMapping];
  
  [stampMapping mapRelationship:@"favorites" withMapping:favoriteMapping];
  
  RKObjectMapping* oauthMapping = [RKObjectMapping mappingForClass:[OAuthToken class]];
  [oauthMapping mapKeyPathsToAttributes:@"access_token", @"accessToken",
   @"refresh_token", @"refreshToken",
   @"expires_in", @"lifetimeSecs", nil];
  
  RKObjectMapping* userAndTokenMapping = [RKObjectMapping serializationMapping];
  [userAndTokenMapping mapRelationship:@"user" withMapping:userMapping];
  [userAndTokenMapping mapRelationship:@"token" withMapping:oauthMapping];
  
  RKObjectMapping* searchResultMapping = [RKObjectMapping mappingForClass:[SearchResult class]];
  [searchResultMapping mapKeyPathsToAttributes:@"entity_id", @"entityID", @"search_id", @"searchID", nil];
  [searchResultMapping mapAttributes:@"category", @"title", @"subtitle", @"distance", nil];
  
  // Example date string: 2011-07-19 20:49:42.037000 OR 2011-07-19 20:49:42
  [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss.SSSSSS" inTimeZone:nil];
  [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss" inTimeZone:nil];
  
  [objectManager.mappingProvider setMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setMapping:stampMapping forKeyPath:@"Stamp"];
  //[objectManager.mappingProvider setMapping:detailedEntityMapping forKeyPath:@"DetailedEntity"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:favoriteMapping forKeyPath:@"Favorite"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];
  [objectManager.mappingProvider setMapping:userAndTokenMapping forKeyPath:@"UserAndToken"];
  [objectManager.mappingProvider setMapping:searchResultMapping forKeyPath:@"SearchResult"];
}


- (void)customizeAppearance {
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
  
  //Root Menu
  NSDictionary* inboxChoices = [NSDictionary dictionaryWithObjectsAndKeys:
                                [STInboxViewController class], @"New Inbox",
                                [STLegacyInboxViewController class], @"Old Inbox",
                                nil];
  [STConfiguration addChoices:inboxChoices originalKey:@"New Inbox" forKey:@"Root.inbox"];
  [STConfiguration addValue:[STIWantToViewController class] forKey:@"Root.iWantTo"];
  [STConfiguration addValue:[STUniversalNewsController class] forKey:@"Root.news"];
  [STConfiguration addValue:[STTodoViewController class] forKey:@"Root.todo"];
  [STConfiguration addValue:[STDebugViewController class] forKey:@"Root.debug"];
  [STConfiguration addValue:[SettingsViewController class] forKey:@"Root.settings"];
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
  [STConfiguration addFont:[UIFont fontWithName:@"Helvetica" size:fontSize] forKey:@"UIFont.stampedFont" inSection:@"UIFont"];
  [STConfiguration addFont:[UIFont fontWithName:@"Helvetica-Bold" size:fontSize] forKey:@"UIFont.stampedBoldFont" inSection:@"UIFont"];
  [STConfiguration addFont:[UIFont fontWithName:@"Helvetica" size:fontSize] forKey:@"UIFont.stampedSubtitleFont" inSection:@"UIFont"];
  
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
  
  // Comments
  [STConfiguration addFont:[UIFont stampedBoldFontWithSize:12] forKey:@"Comments.font"];
  
  //I Want to
  [STIWantToViewController setupConfigurations];
  
  //Stamp Cell
  [STStampCell setupConfigurations];
  
  //Create Stamp
  [STCreateStampViewController setupConfigurations];
}

@end
