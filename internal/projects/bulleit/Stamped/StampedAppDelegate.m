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
static NSString* const kDataBaseURL = @"http://api.stamped.com:5000/api/v1";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
  [TestFlight takeOff:@"ba4288d07f0c453219caeeba7c5007e8_MTg5MDIyMDExLTA4LTMxIDIyOjUyOjE2LjUyNTk3OA"];

  [RKRequestQueue sharedQueue].suspended = YES;
  [RKRequestQueue sharedQueue].concurrentRequestsLimit = 1;
  [RKRequestQueue sharedQueue].delegate = [AccountManager sharedManager];
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDevDataBaseURL];
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
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
                                       nil];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapAttributes:@"bio", @"website", nil];

  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID",
                                         @"opentable_url", @"openTableURL", nil];
  entityMapping.primaryKeyAttribute = @"entityID";
  [entityMapping mapAttributes:@"address", @"category", @"subtitle",
                               @"title", @"coordinates", @"phone", @"subcategory",
                               @"street", @"substreet", @"city", @"state", @"zipcode",
                               @"desc", @"artist", @"album", @"authors",
                               @"cast", @"director", @"year", nil];

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

  // Example date string: 2011-07-19 20:49:42.037000
  NSString* dateFormat = @"yyyy-MM-dd HH:mm:ss.SSSSSS";
  [favoriteMapping.dateFormatStrings addObject:dateFormat];
	[stampMapping.dateFormatStrings addObject:dateFormat];
  [commentMapping.dateFormatStrings addObject:dateFormat];
  [eventMapping.dateFormatStrings addObject:dateFormat];
  
  [objectManager.mappingProvider setMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:favoriteMapping forKeyPath:@"Favorite"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];

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
