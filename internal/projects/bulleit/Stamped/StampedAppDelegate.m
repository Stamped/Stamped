//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampedAppDelegate.h"

#import <RestKit/CoreData/CoreData.h>

#import "Comment.h"
#import "Entity.h"
#import "Stamp.h"
#import "User.h"

static NSString* kDataBaseURL = @"http://api.stamped.com:5000/api/v1";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
  [RKRequestQueue sharedQueue].showsNetworkActivityIndicatorWhenBusy = YES;
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDataBaseURL];

  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  RKManagedObjectMapping* userMapping = [RKManagedObjectMapping mappingForClass:[User class]];
  userMapping.primaryKeyAttribute = @"userID";
  [userMapping mapKeyPathsToAttributes:@"user_id", @"userID",
                                       @"first_name", @"firstName",
                                       @"last_name", @"lastName",
                                       @"display_name", @"displayName",
                                       @"color_primary", @"primaryColor",
                                       @"color_secondary", @"secondaryColor",
                                       @"profile_image", @"profileImageURL",
                                       @"screen_name", @"screenName",
                                       nil];
  [userMapping mapAttributes:@"bio", @"website", nil];
  
  RKManagedObjectMapping* coordinateMapping = [RKManagedObjectMapping mappingForEntityWithName:@"Coordinate"];
  [coordinateMapping mapAttributes:@"lat", @"lng", nil];

  RKManagedObjectMapping* entityMapping = [RKManagedObjectMapping mappingForClass:[Entity class]];
  entityMapping.primaryKeyAttribute = @"entityID";
  [entityMapping mapKeyPathsToAttributes:@"entity_id", @"entityID", nil];
  [entityMapping mapAttributes:@"category", @"subtitle", @"title", nil];
  [entityMapping mapRelationship:@"coordinates" withObjectMapping:coordinateMapping];  

  RKManagedObjectMapping* stampMapping = [RKManagedObjectMapping mappingForClass:[Stamp class]];
  stampMapping.primaryKeyAttribute = @"stampID";
  [stampMapping mapKeyPathsToAttributes:@"stamp_id", @"stampID",
                                        @"last_modified", @"lastModified",
                                        @"num_comments", @"numComments", nil];
  [stampMapping mapAttributes:@"blurb", nil];
  [stampMapping mapKeyPath:@"entity" toRelationship:@"entityObject" withObjectMapping:entityMapping];
  [stampMapping mapRelationship:@"user" withObjectMapping:userMapping];
  
  RKManagedObjectMapping* commentMapping = [RKManagedObjectMapping mappingForClass:[Comment class]];
  commentMapping.primaryKeyAttribute = @"commentID";
  [commentMapping mapAttributes:@"blurb", nil];
  [commentMapping mapKeyPathsToAttributes:@"comment_id", @"commentID",
                                          @"restamp_id", @"restampID",
                                          @"stamp_id", @"stampID",
                                          @"last_modified", @"lastModified", nil];
  [commentMapping mapRelationship:@"user" withObjectMapping:userMapping];
  // Example date string: 2011-07-19 20:49:42.037000
  NSString* dateFormat = @"yyyy-MM-dd HH:mm:ss.SSSSSS";
	[stampMapping.dateFormatStrings addObject:dateFormat];
  [commentMapping.dateFormatStrings addObject:dateFormat];
  
  [objectManager.mappingProvider setObjectMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setObjectMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setObjectMapping:entityMapping forKeyPath:@"Entity"];
  [objectManager.mappingProvider setObjectMapping:commentMapping forKeyPath:@"Comment"];

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

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"loading of object failed: %@", [error localizedDescription]);
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  NSLog(@"current user: %@", (User*)object);
}

@end
