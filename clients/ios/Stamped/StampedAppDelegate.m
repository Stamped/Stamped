//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampedAppDelegate.h"

#import "BWQuincyManager.h"

#import "AccountManager.h"
#import "DetailedEntity.h"
#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "Stamp.h"
#import "User.h"
#import "Notifications.h"
#import "SearchResult.h"
#import "OAuthToken.h"
#import "STNavigationBar.h"
#import "UserImageDownloadManager.h"
#import "UIColor+Stamped.h"
#import "SocialManager.h"
#import "EditEntityViewController.h"

static NSString* const kDevDataBaseURL = @"https://dev.stamped.com/v0";
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface StampedAppDelegate ()
- (void)customizeAppearance;
- (void)performRestKitMappings;
- (void)userSwipedRightOnNavBar:(UISwipeGestureRecognizer*)recognizer;
- (void)handleGridTap:(UIGestureRecognizer*)recognizer;

@property (nonatomic, retain) UIImageView* gridView;
@end

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;
@synthesize gridView = gridView_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
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
  [BWQuincyManager sharedQuincyManager].autoSubmitCrashReport = YES;
  [self performRestKitMappings];
  [self customizeAppearance];
  
  UISwipeGestureRecognizer* swipeRecognizer = [[UISwipeGestureRecognizer alloc] initWithTarget:self
                                                                                        action:@selector(userSwipedRightOnNavBar:)];
  [self.navigationController.navigationBar addGestureRecognizer:swipeRecognizer];
  [swipeRecognizer release];
  self.window.rootViewController = self.navigationController;
  gridView_ = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"column-grid"]];
  gridView_.alpha = 0;
  
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(handleGridTap:)];
  recognizer.numberOfTapsRequired = 3;
  recognizer.numberOfTouchesRequired = 3;
  [self.window addGestureRecognizer:recognizer];
  [recognizer release];
  [window_ addSubview:gridView_];
  [gridView_ release];
  
  UIImageView* corners = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corners_full"]];
  [self.window addSubview:corners];
  [corners release];
  [self.window makeKeyAndVisible];

  NSDictionary* userInfo = [launchOptions valueForKey:UIApplicationLaunchOptionsRemoteNotificationKey];
  NSDictionary* apsInfo = [userInfo objectForKey:@"aps"];
  if (apsInfo) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kPushNotificationReceivedNotification
                                                        object:self
                                                      userInfo:apsInfo];
    [[UIApplication sharedApplication] setApplicationIconBadgeNumber:1];
    [[UIApplication sharedApplication] setApplicationIconBadgeNumber:0];
  }
    
  return YES;
}

#pragma mark - Gesture Recognizers.

- (void)userSwipedRightOnNavBar:(UISwipeGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [self.navigationController popToRootViewControllerAnimated:YES];
}

- (void)handleGridTap:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [UIView animateWithDuration:0.2 animations:^{
    gridView_.alpha = gridView_.alpha == 1 ? 0 : 1;
  }];
}

- (void)applicationWillResignActive:(UIApplication*)application {
  [[UserImageDownloadManager sharedManager] purgeCache];
  gridView_.alpha = 0;
}

- (void)applicationDidReceiveMemoryWarning:(UIApplication*)application {
  [[UserImageDownloadManager sharedManager] purgeCache];
}

- (void)application:(UIApplication*)app didRegisterForRemoteNotificationsWithDeviceToken:(NSData*)devToken {
  if (!devToken || ![AccountManager sharedManager].authenticated)
    return;

  NSString* deviceToken = [NSString stringWithFormat:@"%@", devToken];
  deviceToken = [deviceToken stringByTrimmingCharactersInSet:[NSCharacterSet characterSetWithCharactersInString:@"<>"]];
  deviceToken = [deviceToken stringByReplacingOccurrencesOfString:@" " withString:@""];
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kPushNotificationPath delegate:self];
  request.method = RKRequestMethodPOST;
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:deviceToken, @"token", nil];
  [request send];
}

- (void)application:(UIApplication*)application didReceiveRemoteNotification:(NSDictionary*)userInfo {
  [[NSNotificationCenter defaultCenter] postNotificationName:kPushNotificationReceivedNotification
                                                      object:self
                                                    userInfo:[userInfo objectForKey:@"aps"]];
  [[UIApplication sharedApplication] setApplicationIconBadgeNumber:1];
  [[UIApplication sharedApplication] setApplicationIconBadgeNumber:0];
}

- (void)application:(UIApplication*)app didFailToRegisterForRemoteNotificationsWithError:(NSError*)err {
  NSLog(@"Error in registration. Error: %@", err);
}

- (void)applicationDidEnterBackground:(UIApplication*)application {
  gridView_.alpha = 0;
}

- (void)applicationWillEnterForeground:(UIApplication*)application {}

- (void)applicationDidBecomeActive:(UIApplication*)application {}

- (void)applicationWillTerminate:(UIApplication*)application {
  gridView_.alpha = 0;
}

- (void)dealloc {
  gridView_ = nil;
  [window_ release];
  [navigationController_ release];
  [super dealloc];
}

#pragma mark - Private methods.

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

- (void)performRestKitMappings {
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDataBaseURL];
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  [RKClient sharedClient].requestQueue.delegate = [AccountManager sharedManager];
  [RKClient sharedClient].requestQueue.requestTimeout = 30;
  [RKClient sharedClient].requestQueue.concurrentRequestsLimit = 1;

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
  [objectManager.mappingProvider setMapping:detailedEntityMapping forKeyPath:@"DetailedEntity"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:favoriteMapping forKeyPath:@"Favorite"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];
  [objectManager.mappingProvider setMapping:userAndTokenMapping forKeyPath:@"UserAndToken"];
  [objectManager.mappingProvider setMapping:searchResultMapping forKeyPath:@"SearchResult"];
}

#pragma mark - UIApplicationDelegate methods.

// Pre 4.2 support
- (BOOL)application:(UIApplication*)application handleOpenURL:(NSURL*)url {
  return [[SocialManager sharedManager] handleOpenURLFromFacebook:url]; 
}

// For 4.2+ support
- (BOOL)application:(UIApplication*)application openURL:(NSURL*)url
  sourceApplication:(NSString*)sourceApplication annotation:(id)annotation {
  return [[SocialManager sharedManager] handleOpenURLFromFacebook:url];
}

@end
