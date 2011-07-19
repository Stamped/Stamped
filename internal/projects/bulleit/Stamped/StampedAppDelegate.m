//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampedAppDelegate.h"

#import <RestKit/CoreData/CoreData.h>

#import "Stamp.h"

static NSString* kDataBaseURL = @"http://50.19.163.247:5000/api/v1";

@implementation StampedAppDelegate

@synthesize window = window_;
@synthesize navigationController = navigationController_;

- (BOOL)application:(UIApplication*)application didFinishLaunchingWithOptions:(NSDictionary*)launchOptions {
#if 0
  RKLogConfigureByName("RestKit/ObjectMapping", RKLogLevelDebug);
  [RKRequestQueue sharedQueue].showsNetworkActivityIndicatorWhenBusy = YES;
  RKObjectManager* objectManager = [RKObjectManager objectManagerWithBaseURL:kDataBaseURL];
  
  objectManager.objectStore = [RKManagedObjectStore objectStoreWithStoreFilename:@"StampedData.sqlite"];
  RKManagedObjectMapping* accountMapping = [RKManagedObjectMapping mappingForEntityWithName:@"Account"];
  accountMapping.primaryKeyAttribute = @"userID";
  [accountMapping mapKeyPathsToAttributes:@"user_id", @"userID",
                                          @"first_name", @"firstName",
                                          @"last_name", @"lastName",
                                          @"display_name", @"displayName",
                                          nil];
  [accountMapping mapAttributes:@"bio", @"website", @"email", nil];
  
  RKManagedObjectMapping* stampMapping = [RKManagedObjectMapping mappingForClass:[Stamp class]];
  stampMapping.primaryKeyAttribute = @"stampID";
  [stampMapping mapKeyPathsToAttributes:@"stamp_id", @"stampID", nil];
  [stampMapping mapAttributes:@"title", @"subtitle", nil];
  //[stampMapping mapRelationship:@"user" withObjectMapping:accountMapping];
  
  [objectManager.mappingProvider setObjectMapping:accountMapping forKeyPath:@"Account"];
  [objectManager.mappingProvider setObjectMapping:stampMapping forKeyPath:@"Stamp"];
  
  
  [objectManager loadObjectsAtResourcePath:@"/users/show.json?screen_name=sample_andybons" objectMapping:accountMapping delegate:self];
  [objectManager loadObjectsAtResourcePath:@"/collections/inbox.json?authenticated_user_id=4e24db9332a7ba42ec000006" objectMapping:stampMapping delegate:self];
#endif

  self.window.rootViewController = self.navigationController;
  [self.window makeKeyAndVisible];
  return YES;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"LastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
	NSLog(@"Loaded stamps: %@", objects);
	//[self loadObjectsFromDataStore];
	//[_tableView reloadData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Error" 
                                                   message:[error localizedDescription] 
                                                  delegate:nil 
                                         cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease];
	[alert show];
	NSLog(@"Hit error: %@", error);
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
