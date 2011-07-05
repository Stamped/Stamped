//
//  StampedMockBAppDelegate.m
//  StampedMockB
//
//  Created by Kevin Palms on 6/27/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "StampedMockBAppDelegate.h"
#import "InboxAViewController.h"
#import "Stamp.h"

@implementation StampedMockBAppDelegate


@synthesize window=_window;

@synthesize managedObjectContext=__managedObjectContext;

@synthesize managedObjectModel=__managedObjectModel;

@synthesize persistentStoreCoordinator=__persistentStoreCoordinator;

- (void)buildTestStamps
{
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Ramen Takumi", @"title",
                           @"Good ramen near Union Square.", @"comment",
                           @"jake", @"avatar",
                           @"1", @"userID",
                           @"jake", @"stampImage",
                           [NSNumber numberWithBool:YES], @"hasPhoto",
                           @"place", @"category",
                           @"New York, NY", @"subTitle",
                           [UIColor colorWithRed:(208/255.0) green:(83/255.0) blue:(83/255.0) alpha:1], @"color",
                           @"Jake Z.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Freedom", @"title",
                           @"Best book I've read all year. And I read a lot.", @"comment",
                           @"paul", @"avatar",
                           @"2", @"userID",
                           @"paul", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"Jonathan Franzen", @"subTitle",
                           @"book", @"category",
                           [UIColor colorWithRed:0.98824 green:0.75294 blue:0.19608 alpha:1], @"color",
                           @"Paul S.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Super 8", @"title",
                           @"Wasn't expecting much, but it's fantastic. Reminds me of Lost (in a good way).", @"comment",
                           @"kevin", @"avatar",
                           @"4", @"userID",
                           @"kevin", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"Thriller", @"subTitle",
                           @"movie", @"category",
                           [UIColor colorWithRed:(129/255.0) green:(166/255.0) blue:(179/255.0) alpha:1], @"color",
                           @"Kevin P.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Subway", @"title",
                           @"Extremely jealous that Travis has a $200 gift card here.", @"comment",
                           @"robby", @"avatar",
                           @"3", @"userID",
                           @"robby", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"New York, NY", @"subTitle",
                           @"place", @"category",
                           [UIColor colorWithRed:(151/255.0) green:(87/255.0) blue:(178/255.0) alpha:1], @"color",
                           @"Robby S.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Liveview", @"title",
                           @"I tried to give the developer money, but couldn't figure out how. Still, very useful app.", @"comment",
                           @"ed", @"avatar",
                           @"6", @"userID",
                           @"ed", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"iPhone App", @"subTitle",
                           @"app", @"category",
                           [UIColor colorWithRed:(83/255.0) green:(147/255.0) blue:(211/255.0) alpha:1], @"color",
                           @"Ed K.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Kimchi Taco Truck", @"title",
                           @"Tuesdays on 23rd and Broadway. Pork tacos are the best.", @"comment",
                           @"kevin", @"avatar",
                           @"4", @"userID",
                           @"kevin", @"stampImage",
                           [NSNumber numberWithBool:YES], @"hasPhoto",
                           @"New York, NY", @"subTitle",
                           @"place", @"category",
                           [UIColor colorWithRed:(129/255.0) green:(166/255.0) blue:(179/255.0) alpha:1], @"color",
                           @"Kevin P.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Telephasic Workshop", @"title",
                           @"I listen to this all day.", @"comment",
                           @"jake", @"avatar",
                           @"1", @"userID",
                           @"jake", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"music", @"category",
                           @"Boards of Canada", @"subTitle",
                           [UIColor colorWithRed:(208/255.0) green:(83/255.0) blue:(83/255.0) alpha:1], @"color",
                           @"Jake Z.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Wu Lyf - Go Tell Fire To The Mountain", @"title",
                           @"Awesome album. On repeat all weekend.", @"comment",
                           @"ed", @"avatar",
                           @"6", @"userID",
                           @"ed", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"New York, NY", @"subTitle",
                           @"place", @"category",
                           [UIColor colorWithRed:(83/255.0) green:(147/255.0) blue:(211/255.0) alpha:1], @"color",
                           @"Ed K.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
  
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"Raines Law Room", @"title",
                           @"Cocktails are amazing at this speakeasy. I love my bourbon.", @"comment",
                           @"robby", @"avatar",
                           @"3", @"userID",
                           @"robby", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           @"New York, NY", @"subTitle",
                           @"place", @"category",
                           [UIColor colorWithRed:(151/255.0) green:(87/255.0) blue:(178/255.0) alpha:1], @"color",
                           @"Robby S.", @"userName",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	/*
   [Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
   @"Gramercy Tavern", @"title",
   @"The lamb is phenomenal and the service is impeccable. Lovely.", @"comment",
   @"cheryl", @"avatar",
   @"5", @"userID",
   @"cheryl", @"stampImage",
   [NSNumber numberWithBool:NO], @"hasPhoto",
   nil] 
   inManagedObjectContext:self.managedObjectContext];
   
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"X-Men: First Class", @"title",
                           @"If you like X-Men you should go see this. So much fun.", @"comment",
                           @"bart", @"avatar",
                           @"7", @"userID",
                           @"bart", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
	
	[Stamp addStampWithData:[NSDictionary dictionaryWithObjectsAndKeys:
                           @"QuickBooks", @"title",
                           @"What's this app for again?", @"comment",
                           @"bart", @"avatar",
                           @"7", @"userID",
                           @"bart", @"stampImage",
                           [NSNumber numberWithBool:NO], @"hasPhoto",
                           nil] 
   inManagedObjectContext:self.managedObjectContext];
  */
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
  [self buildTestStamps];
	// Build Inbox and Load
	//InboxTableViewController *inboxvc = [[InboxTableViewController alloc] initInManagedObjectContext:self.managedObjectContext];
	InboxAViewController *inboxvc = [[InboxAViewController alloc] initInManagedObjectContext:self.managedObjectContext];
	
	UINavigationController *nav = [[UINavigationController alloc] init];
	[nav pushViewController:inboxvc animated:NO];
	[inboxvc release];
	
	[self.window addSubview:nav.view];
  [self.window makeKeyAndVisible];
  
  return YES;
}

- (void)applicationWillResignActive:(UIApplication *)application
{
  /*
   Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
   Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
   */
}

- (void)applicationDidEnterBackground:(UIApplication *)application
{
  /*
   Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
   If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
   */
}

- (void)applicationWillEnterForeground:(UIApplication *)application
{
  /*
   Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
   */
}

- (void)applicationDidBecomeActive:(UIApplication *)application
{
  /*
   Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
   */
}

- (void)applicationWillTerminate:(UIApplication *)application
{
  // Saves changes in the application's managed object context before the application terminates.
  [self saveContext];
}

- (void)dealloc
{
  [_window release];
  [__managedObjectContext release];
  [__managedObjectModel release];
  [__persistentStoreCoordinator release];
    [super dealloc];
}

- (void)awakeFromNib
{
    /*
     Typically you should set up the Core Data stack here, usually by passing the managed object context to the first view controller.
     self.<#View controller#>.managedObjectContext = self.managedObjectContext;
    */
}

- (void)saveContext
{
    NSError *error = nil;
    NSManagedObjectContext *managedObjectContext = self.managedObjectContext;
    if (managedObjectContext != nil)
    {
        if ([managedObjectContext hasChanges] && ![managedObjectContext save:&error])
        {
            /*
             Replace this implementation with code to handle the error appropriately.
             
             abort() causes the application to generate a crash log and terminate. You should not use this function in a shipping application, although it may be useful during development. If it is not possible to recover from the error, display an alert panel that instructs the user to quit the application by pressing the Home button.
             */
            NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
            abort();
        } 
    }
}

#pragma mark - Core Data stack

/**
 Returns the managed object context for the application.
 If the context doesn't already exist, it is created and bound to the persistent store coordinator for the application.
 */
- (NSManagedObjectContext *)managedObjectContext
{
    if (__managedObjectContext != nil)
    {
        return __managedObjectContext;
    }
    
    NSPersistentStoreCoordinator *coordinator = [self persistentStoreCoordinator];
    if (coordinator != nil)
    {
        __managedObjectContext = [[NSManagedObjectContext alloc] init];
        [__managedObjectContext setPersistentStoreCoordinator:coordinator];
    }
    return __managedObjectContext;
}

/**
 Returns the managed object model for the application.
 If the model doesn't already exist, it is created from the application's model.
 */
- (NSManagedObjectModel *)managedObjectModel
{
    if (__managedObjectModel != nil)
    {
        return __managedObjectModel;
    }
    NSURL *modelURL = [[NSBundle mainBundle] URLForResource:@"StampedMockB" withExtension:@"momd"];
    __managedObjectModel = [[NSManagedObjectModel alloc] initWithContentsOfURL:modelURL];    
    return __managedObjectModel;
}

/**
 Returns the persistent store coordinator for the application.
 If the coordinator doesn't already exist, it is created and the application's store added to it.
 */
- (NSPersistentStoreCoordinator *)persistentStoreCoordinator
{
    if (__persistentStoreCoordinator != nil)
    {
        return __persistentStoreCoordinator;
    }
    
    NSURL *storeURL = [[self applicationDocumentsDirectory] URLByAppendingPathComponent:@"StampedMockB.sqlite"];
    
    NSError *error = nil;
    __persistentStoreCoordinator = [[NSPersistentStoreCoordinator alloc] initWithManagedObjectModel:[self managedObjectModel]];
    if (![__persistentStoreCoordinator addPersistentStoreWithType:NSSQLiteStoreType configuration:nil URL:storeURL options:nil error:&error])
    {
        /*
         Replace this implementation with code to handle the error appropriately.
         
         abort() causes the application to generate a crash log and terminate. You should not use this function in a shipping application, although it may be useful during development. If it is not possible to recover from the error, display an alert panel that instructs the user to quit the application by pressing the Home button.
         
         Typical reasons for an error here include:
         * The persistent store is not accessible;
         * The schema for the persistent store is incompatible with current managed object model.
         Check the error message to determine what the actual problem was.
         
         
         If the persistent store is not accessible, there is typically something wrong with the file path. Often, a file URL is pointing into the application's resources directory instead of a writeable directory.
         
         If you encounter schema incompatibility errors during development, you can reduce their frequency by:
         * Simply deleting the existing store:
         [[NSFileManager defaultManager] removeItemAtURL:storeURL error:nil]
         
         * Performing automatic lightweight migration by passing the following dictionary as the options parameter: 
         [NSDictionary dictionaryWithObjectsAndKeys:[NSNumber numberWithBool:YES], NSMigratePersistentStoresAutomaticallyOption, [NSNumber numberWithBool:YES], NSInferMappingModelAutomaticallyOption, nil];
         
         Lightweight migration will only work for a limited set of schema changes; consult "Core Data Model Versioning and Data Migration Programming Guide" for details.
         
         */
        NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
        abort();
    }    
    
    return __persistentStoreCoordinator;
}

#pragma mark - Application's Documents directory

/**
 Returns the URL to the application's Documents directory.
 */
- (NSURL *)applicationDocumentsDirectory
{
    return [[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask] lastObject];
}

@end
