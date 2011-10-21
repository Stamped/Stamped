//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampedAppDelegate.h"

#import <RestKit/CoreData/CoreData.h>

#import "TestFlight.h"

#import "AccountManager.h"
#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "Stamp.h"
#import "User.h"
#import "Notifications.h"
#import "SearchResult.h"
#import "OAuthToken.h"
#import "UserImageDownloadManager.h"

static NSString* const kDevDataBaseURL = @"https://dev.stamped.com/v0";
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface StampedAppDelegate ()
- (void)performRestKitMappings;
@end

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
#if !TARGET_IPHONE_SIMULATOR
//  [TestFlight takeOff:@"ba4288d07f0c453219caeeba7c5007e8_MTg5MDIyMDExLTA4LTMxIDIyOjUyOjE2LjUyNTk3OA"];
#endif
  [self performRestKitMappings];
  self.window.rootViewController = self.navigationController;
  [self.window makeKeyAndVisible];

  NSDictionary* userInfo = [launchOptions valueForKey:UIApplicationLaunchOptionsRemoteNotificationKey];
  NSDictionary* apsInfo = [userInfo objectForKey:@"aps"];
  if (apsInfo) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kPushNotificationReceivedNotification 
                                                        object:self
                                                      userInfo:apsInfo];
    [UIApplication sharedApplication].applicationIconBadgeNumber = 0;
  }

  return YES;
}

- (void)applicationWillResignActive:(UIApplication*)application {
  [[UserImageDownloadManager sharedManager] purgeCache];
}

- (void)applicationDidReceiveMemoryWarning:(UIApplication*)application {
  [[UserImageDownloadManager sharedManager] purgeCache];
}

- (void)application:(UIApplication*)app didRegisterForRemoteNotificationsWithDeviceToken:(NSData*)devToken {
  NSString* deviceToken = [NSString stringWithFormat:@"%@", devToken];
  deviceToken = [deviceToken stringByTrimmingCharactersInSet:[NSCharacterSet characterSetWithCharactersInString:@"<>"]];
  deviceToken = [deviceToken stringByReplacingOccurrencesOfString:@" " withString:@""];
  
  NSLog(@"Device token: %@", deviceToken);
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:kPushNotificationPath delegate:self];
  request.method = RKRequestMethodPOST;
  request.params = [NSDictionary dictionaryWithObjectsAndKeys:deviceToken, @"token", nil];
  [request send];
}

- (void)application:(UIApplication*)application didReceiveRemoteNotification:(NSDictionary*)userInfo {
  [[NSNotificationCenter defaultCenter] postNotificationName:kPushNotificationReceivedNotification
                                                      object:self
                                                    userInfo:[userInfo objectForKey:@"aps"]];
  [UIApplication sharedApplication].applicationIconBadgeNumber = 0;
}

- (void)application:(UIApplication*)app didFailToRegisterForRemoteNotificationsWithError:(NSError*)err {
  NSLog(@"Error in registration. Error: %@", err);
}

- (void)applicationDidEnterBackground:(UIApplication*)application {}

- (void)applicationWillEnterForeground:(UIApplication*)application {}

- (void)applicationDidBecomeActive:(UIApplication*)application {}

- (void)applicationWillTerminate:(UIApplication*)application {}

- (void)dealloc {
  [window_ release];
  [navigationController_ release];
  [super dealloc];
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  NSLog(@"Push nofification registration response: %@", response.bodyAsString);
}

#pragma mark - Private methods.

- (void)performRestKitMappings {
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDevDataBaseURL];
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
     @"image_url", @"imageURL",
     nil];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapAttributes:@"bio", @"website", @"location", nil];
  
  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID",
     @"opentable_url", @"openTableURL",
     @"itunes_short_url", @"itunesShortURL",
     @"itunes_url", @"itunesURL",
     @"artist_name", @"artist",
     @"release_date", @"releaseDate",
     @"amazon_url", @"amazonURL",
     @"in_theaters", @"inTheaters",
     @"fandango_url", @"fandangoURL", nil];
  
  entityMapping.primaryKeyAttribute = @"entityID";
  [entityMapping mapAttributes:@"address", @"category", @"subtitle",
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
  [stampMapping mapAttributes:@"blurb", @"modified", nil];
  [stampMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [stampMapping mapRelationship:@"user" withMapping:userMapping];
  [stampMapping mapKeyPath:@"comment_preview" toRelationship:@"comments" withMapping:commentMapping];
  [stampMapping mapKeyPath:@"credit" toRelationship:@"credits" withMapping:userMapping];
  
  [userMapping mapRelationship:@"credits" withMapping:stampMapping];
  
  RKManagedObjectMapping* eventMapping = [RKManagedObjectMapping mappingForClass:[Event class]];
  [eventMapping mapAttributes:@"created", @"genre", @"subject", @"blurb", @"benefit", nil];
  [eventMapping mapKeyPath:@"activity_id" toAttribute:@"eventID"];
  [eventMapping mapKeyPath:@"linked_url" toAttribute:@"URL"];
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
  
  // Example date string: 2011-07-19 20:49:42.037000
  [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss.SSSSSS" inTimeZone:nil];
  
  [objectManager.mappingProvider setMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:favoriteMapping forKeyPath:@"Favorite"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];
  [objectManager.mappingProvider setMapping:userAndTokenMapping forKeyPath:@"UserAndToken"];
  
  [objectManager.mappingProvider setMapping:searchResultMapping forKeyPath:@"SearchResult"];
}

@end
