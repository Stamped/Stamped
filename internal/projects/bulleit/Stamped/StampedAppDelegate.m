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

#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "Stamp.h"
#import "User.h"
#import "OAuthToken.h"

static NSString* kDataBaseURL = @"http://api.stamped.com:5000/api/v1";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
  [RKRequestQueue sharedQueue].showsNetworkActivityIndicatorWhenBusy = YES;
  [RKRequestQueue sharedQueue].concurrentRequestsLimit = 1;
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDataBaseURL];
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  RKManagedObjectMapping* userMapping = [RKManagedObjectMapping mappingForClass:[User class]];
  [userMapping mapKeyPathsToAttributes:@"user_id", @"userID",
                                       @"first_name", @"firstName",
                                       @"last_name", @"lastName",
                                       @"display_name", @"displayName",
                                       @"color_primary", @"primaryColor",
                                       @"color_secondary", @"secondaryColor",
                                       @"profile_image", @"profileImageURL",
                                       @"screen_name", @"screenName",
                                       nil];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapAttributes:@"bio", @"website", nil];

  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID",
                                         @"opentable_url", @"openTableURL", nil];
  entityMapping.primaryKeyAttribute = @"entityID";
  [entityMapping mapAttributes:@"address", @"category", @"subtitle",
                               @"title", @"coordinates", @"phone", nil];

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
                                        @"num_comments", @"numComments", nil];
  stampMapping.primaryKeyAttribute = @"stampID";
  [stampMapping mapAttributes:@"blurb", nil];
  [stampMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withMapping:entityMapping];
  [stampMapping mapRelationship:@"user" withMapping:userMapping];
  [stampMapping mapKeyPath:@"comment_preview" toRelationship:@"comments" withMapping:commentMapping];
  
  RKManagedObjectMapping* eventMapping = [RKManagedObjectMapping mappingForClass:[Event class]];
  [eventMapping mapAttributes:@"created", @"genre", nil];
  [eventMapping mapKeyPath:@"activity_id" toAttribute:@"eventID"];
  eventMapping.primaryKeyAttribute = @"eventID";
  [eventMapping mapRelationship:@"comment" withMapping:commentMapping];
  [eventMapping mapRelationship:@"stamp" withMapping:stampMapping];
  [eventMapping mapRelationship:@"user" withMapping:userMapping];
  
  RKObjectMapping* oauthMapping = [RKObjectMapping mappingForClass:[OAuthToken class]];
  [oauthMapping mapKeyPathsToAttributes:@"access_token", @"accessToken",
                                        @"refresh_token", @"refreshToken",
                                        @"expires_in", @"lifetimeSecs", nil];

  // Example date string: 2011-07-19 20:49:42.037000
  NSString* dateFormat = @"yyyy-MM-dd HH:mm:ss.SSSSSS";
	[stampMapping.dateFormatStrings addObject:dateFormat];
  [commentMapping.dateFormatStrings addObject:dateFormat];
  [eventMapping.dateFormatStrings addObject:dateFormat];
  
  [objectManager.mappingProvider setMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setMapping:commentMapping forKeyPath:@"Comment"];
  [objectManager.mappingProvider setMapping:eventMapping forKeyPath:@"Event"];
  [objectManager.mappingProvider setMapping:oauthMapping forKeyPath:@"OAuthToken"];

  self.window.rootViewController = self.navigationController;
  [self.window makeKeyAndVisible];
  
  return YES;
}

- (void)applicationWillResignActive:(UIApplication*)application {
}

- (void)applicationDidEnterBackground:(UIApplication*)application {
}

- (void)applicationWillEnterForeground:(UIApplication*)application {
}

- (void)applicationDidBecomeActive:(UIApplication*)application {
}

- (void)applicationWillTerminate:(UIApplication*)application {
}

- (void)dealloc {
  [window_ release];
  [navigationController_ release];
  [super dealloc];
}

@end
