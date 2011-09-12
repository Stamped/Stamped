//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampedAppDelegate.h"

#import <RestKit/RestKit.h>
#import <RestKit/CoreData/CoreData.h>

#import "TestFlight.h"

#import "AccountManager.h"
#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "Favorite.h"
#import "Stamp.h"
#import "User.h"
#import "OAuthToken.h"

static NSString* const kDevDataBaseURL = @"https://dev.stamped.com/v0";
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
#if !TARGET_IPHONE_SIMULATOR
  [TestFlight takeOff:@"ba4288d07f0c453219caeeba7c5007e8_MTg5MDIyMDExLTA4LTMxIDIyOjUyOjE2LjUyNTk3OA"];
#endif
  
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDevDataBaseURL];
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  [RKClient sharedClient].requestQueue.suspended = YES;
  [RKClient sharedClient].requestQueue.concurrentRequestsLimit = 1;
  [RKClient sharedClient].requestQueue.delegate = [AccountManager sharedManager];

  RKManagedObjectMapping* userMapping = [RKManagedObjectMapping mappingForClass:[User class]];
  [userMapping mapKeyPathsToAttributes:@"user_id", @"userID",
                                       @"name", @"name",
                                       @"color_primary", @"primaryColor",
                                       @"color_secondary", @"secondaryColor",
                                       @"screen_name", @"screenName",
                                       @"num_credits", @"numCredits",
                                       @"num_followers", @"numFollowers",
                                       @"num_friends", @"numFriends",
                                       @"num_stamps_left", @"numStamps",
                                       nil];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapAttributes:@"bio", @"website", nil];

  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID",
                                         @"opentable_url", @"openTableURL", 
                                         @"itunes_short_url", @"itunesShortURL",
                                         @"itunes_url", @"itunesURL", 
                                         @"artist_name", @"artist",
                                         @"album_name", @"album", 
                                         @"release_date", @"releaseDate", 
                                         @"track_list", @"trackList", 
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
                               @"publisher", @"language", nil];

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
                                        @"image_dimensions", @"imageDimensions",
                                        @"image_url", @"imageURL", nil];
  stampMapping.primaryKeyAttribute = @"stampID";
  [stampMapping mapAttributes:@"blurb", nil];
  [stampMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [stampMapping mapRelationship:@"user" withMapping:userMapping];
  [stampMapping mapKeyPath:@"comment_preview" toRelationship:@"comments" withMapping:commentMapping];
  [stampMapping mapKeyPath:@"credit" toRelationship:@"credits" withMapping:userMapping];
  
  [userMapping mapRelationship:@"credits" withMapping:stampMapping];
  
  RKManagedObjectMapping* eventMapping = [RKManagedObjectMapping mappingForClass:[Event class]];
  [eventMapping mapAttributes:@"created", @"genre", nil];
  [eventMapping mapKeyPath:@"activity_id" toAttribute:@"eventID"];
  eventMapping.primaryKeyAttribute = @"eventID";
  [eventMapping mapRelationship:@"comment" withMapping:commentMapping];
  [eventMapping mapRelationship:@"stamp" withMapping:stampMapping];
  [eventMapping mapRelationship:@"user" withMapping:userMapping];
  
  RKManagedObjectMapping* favoriteMapping = [RKManagedObjectMapping mappingForClass:[Favorite class]];
  [favoriteMapping mapAttributes:@"complete", @"created", nil];
  [favoriteMapping mapKeyPathsToAttributes:@"favorite_id", @"favoriteID",
                                           @"user_id", @"userID", nil];
  favoriteMapping.primaryKeyAttribute = @"favoriteID";
  [favoriteMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [favoriteMapping mapRelationship:@"stamp" withMapping:stampMapping];
  
  [stampMapping mapRelationship:@"favorites" withMapping:favoriteMapping];
  
  RKObjectMapping* oauthMapping = [RKObjectMapping mappingForClass:[OAuthToken class]];
  [oauthMapping mapKeyPathsToAttributes:@"access_token", @"accessToken",
                                        @"refresh_token", @"refreshToken",
                                        @"expires_in", @"lifetimeSecs", nil];

  RKObjectMapping* registerMapping = [RKObjectMapping serializationMapping];
  [registerMapping mapRelationship:@"user" withMapping:userMapping];
  [registerMapping mapRelationship:@"token" withMapping:oauthMapping];

  // Example date string: 2011-07-19 20:49:42.037000
  [RKManagedObjectMapping addDefaultDateFormatterForString:@"yyyy-MM-dd HH:mm:ss.SSSSSS" inTimeZone:nil];
  
  [objectManager.mappingProvider setMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:favoriteMapping forKeyPath:@"Favorite"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];
  [objectManager.mappingProvider setMapping:registerMapping forKeyPath:@"Registration"];

  self.window.rootViewController = self.navigationController;
  [self.window makeKeyAndVisible];

  return YES;
}

/*- (void)applicationWillResignActive:(UIApplication*)application {
}

- (void)applicationDidEnterBackground:(UIApplication*)application {
}

- (void)applicationWillEnterForeground:(UIApplication*)application {
}

- (void)applicationDidBecomeActive:(UIApplication*)application {
}

- (void)applicationWillTerminate:(UIApplication*)application {
}*/

- (void)dealloc {
  [window_ release];
  [navigationController_ release];
  [super dealloc];
}

@end
