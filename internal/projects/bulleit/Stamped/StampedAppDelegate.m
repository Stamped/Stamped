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

#import "Entity.h"
#import "Stamp.h"
#import "User.h"

static NSString* kDataBaseURL = @"http://192.168.0.10:5000/api/v1";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
  // RKLogConfigureByName("RestKit/ObjectMapping", RKLogLevelDebug);
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
  
  // Example date string: 2011-07-19 20:49:42.037000
	[stampMapping.dateFormatStrings addObject:@"yyyy-MM-dd HH:mm:ss.SSSSSS"];
  NSDate* now = [NSDate date];
  NSDateFormatter* weekday = [[[NSDateFormatter alloc] init] autorelease];
  [weekday setDateFormat: @"yyyy-MM-dd HH:mm:ss.SSSSSS"];
  NSLog(@"The day of the week is: %@", [weekday stringFromDate:now]);
  
  [objectManager.mappingProvider setObjectMapping:userMapping forKeyPath:@"User"];
  [objectManager.mappingProvider setObjectMapping:stampMapping forKeyPath:@"Stamp"];
  [objectManager.mappingProvider setObjectMapping:entityMapping forKeyPath:@"Entity"];


  self.window.rootViewController = self.navigationController;
  [self.window makeKeyAndVisible];
  return YES;
}

- (void)applicationWillResignActive:(UIApplication*)application {
  /*
   Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
   Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
   */
}

- (void)applicationDidEnterBackground:(UIApplication*)application {
  /*
   Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
   If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
   */
}

- (void)applicationWillEnterForeground:(UIApplication*)application {
  /*
   Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
   */
}

- (void)applicationDidBecomeActive:(UIApplication*)application {
  /*
   Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
   */
}

- (void)applicationWillTerminate:(UIApplication*)application {
  /*
   Called when the application is about to terminate.
   Save data if appropriate.
   See also applicationDidEnterBackground:.
   */
}

- (void)dealloc {
  [window_ release];
  [navigationController_ release];
  [super dealloc];
}

@end
