//
//  StampedAppDelegate.m
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "StampedAppDelegate.h"
#import "InboxViewController.h"
#import "User.h"
#import "Stamp.h"


@implementation StampedAppDelegate

@synthesize window;


#pragma mark -
#pragma mark Application lifecycle

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {    
    
    // Override point for customization after application launch.
	
	[User addUserWithId:[NSNumber numberWithInt:1] withName:@"Kevin Palms" inManagedObjectContext:self.managedObjectContext];
	[User addUserWithId:[NSNumber numberWithInt:2] withName:@"Robby Stein" inManagedObjectContext:self.managedObjectContext];
	[User addUserWithId:[NSNumber numberWithInt:3] withName:@"Bart Stein" inManagedObjectContext:self.managedObjectContext];
	[User addUserWithId:[NSNumber numberWithInt:4] withName:@"Julia Chen" inManagedObjectContext:self.managedObjectContext];
    
	// Add Stamps
	NSDateFormatter *dateFormat = [[NSDateFormatter alloc] init];
	[dateFormat setDateFormat:@"yyyy-MM-dd"];
	
	
	/** TEMPLATE
	NSDictionary *stamp6 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"", @"stampType", 
							@"", @"title", 
							[dateFormat dateFromString:@"2010-10-03"], @"dateStamped", 
							@"", @"address", 
							@"", @"message", 
							@"", @"urlWebsite",
							nil];
	 */
	
	
	
	//////// ROBBY

	NSDictionary *stamp201 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Eat", @"stampType",
							@"Resto", @"title",
							[dateFormat dateFromString:@"2010-12-29"], @"dateStamped",
							@"Belgian Egg Pasta. I crave this every time I even think about brunch. Still one of the best finds in the city.", @"message",
							nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:201] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp201
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp202 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Play", @"stampType",
							@"Cut The Rope", @"title",
							[dateFormat dateFromString:@"2010-11-15"], @"dateStamped",
							@"one of the most addictive games ever", @"message",
							@"http://itunes.apple.com/us/app/cut-the-rope/id380293530?mt=8", @"urlWebsite",
							nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:202] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp202
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp203 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"The Breslin", @"title",
							  [dateFormat dateFromString:@"2010-10-03"], @"dateStamped",
							  @"get the lamb burger", @"message",
							  @"16 West 29th St, New York 10001", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:203] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp203
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp204 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Boqueria", @"title",
							  [dateFormat dateFromString:@"2010-02-26"], @"dateStamped",
							  @"get any tapas with pork", @"message",
							  @"171 Sprint St, NY 10012", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:204] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp204
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp205 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Sant Ambroeus", @"title",
							  [dateFormat dateFromString:@"2010-07-20"], @"dateStamped",
							  @"Delicious crab spaghetti", @"message",
							  @"259 W 4th St, NYC 10014", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:205] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp205
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp206 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Hotel Griffou", @"title",
							  [dateFormat dateFromString:@"2010-08-10"], @"dateStamped",
							  @"Incredible lobster fettuccine", @"message",
							  @"21 W 9th St, NYC 10011", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:206] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp206
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp207 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Spotted Pig", @"title",
							  [dateFormat dateFromString:@"2011-01-24"], @"dateStamped",
							  @"One of the best burgers in NYC", @"message",
							  @"314 W 11th St, NYC 10014", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:207] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp207
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp208 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"L'Artusi", @"title",
							  [dateFormat dateFromString:@"2010-09-04"], @"dateStamped",
							  @"Homemade mushroom pasta", @"message",
							  @"228 W 10th St, NYC 10014", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:208] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp208
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp209 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Drink", @"stampType", 
							  @"Cerasuolo di Vittoria 2008", @"title",
							  [dateFormat dateFromString:@"2010-10-13"], @"dateStamped",
							  @"best red wine I've had to date", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:209] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp209
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp210 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Visit", @"stampType", 
							  @"Empire Hotel", @"title",
							  [dateFormat dateFromString:@"2010-10-18"], @"dateStamped",
							  @"Great price and quality hotel in upper west side", @"message",
							  @"44 W 63rd St, NYC 10023", @"address", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:210] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp210
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp211 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Buy", @"stampType", 
							  @"Vizio TV", @"title",
							  [dateFormat dateFromString:@"2009-08-13"], @"dateStamped",
							  @"best price to qualito ratio I can find", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:211] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp211
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	NSDictionary *stamp212 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Watch", @"stampType", 
							  @"The Fighter", @"title",
							  [dateFormat dateFromString:@"2010-12-28"], @"dateStamped",
							  @"favorite movie of the winter, but haven't seen King's Speech ;)", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:212] 
				 fromUser:[NSNumber numberWithInt:2] 
				 withData:stamp212
   inManagedObjectContext:self.managedObjectContext]; 
	
	
	
	
	
	//////// BART
	
	NSDictionary *stamp301 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Eat", @"stampType", 
							@"Commerce", @"title", 
							[dateFormat dateFromString:@"2010-12-28"], @"dateStamped", 
							@"50 Commerce Street NYC 10014", @"address", 
							@"roast chicken and bread basket are amazing", @"message", 
							nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:301] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp301
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp302 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Read", @"stampType", 
							@"Winning the War, Losing the Peace", @"title", 
							[dateFormat dateFromString:@"2010-03-02"], @"dateStamped", 
							@"Ayad Allawi", @"author", 
							@"Best, most informative book on Iraq war I've ever read", @"message", 
							nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:302] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp302
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp303 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Play", @"stampType", 
							@"NBA 2k11 (PS3)", @"title", 
							[dateFormat dateFromString:@"2010-11-22"], @"dateStamped",  
							@"More realistic than playing real basketball", @"message", 
							nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:303] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp303
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp304 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Neptune Oyster Bar", @"title", 
							  [dateFormat dateFromString:@"2010-09-10"], @"dateStamped", 
							  @"63 Salem St, Boston 02113", @"address", 
							  @"Best lobster roll I've ever had. Get it hot.", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:304] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp304
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp305 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Marlow and Sons", @"title", 
							  [dateFormat dateFromString:@"2010-10-10"], @"dateStamped", 
							  @"81 Broadway, NYC 11211", @"address", 
							  @"meat plate. done.", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:305] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp305
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp306 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Drink", @"stampType", 
							  @"Macallan 12 yr", @"title", 
							  [dateFormat dateFromString:@"2010-12-02"], @"dateStamped", 
							  @"Scotch of choice", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:306] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp306
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp307 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"The Tipsy Pig", @"title", 
							  [dateFormat dateFromString:@"2011-01-23"], @"dateStamped", 
							  @"2231 Chestnut St, San Francisco 94123", @"address", 
							  @"Burger is epic", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:307] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp307
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp308 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Watch", @"stampType", 
							  @"Groundhog Day", @"title", 
							  [dateFormat dateFromString:@"2010-09-29"], @"dateStamped", 
							  @"One of my all time favorites", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:308] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp308
   inManagedObjectContext:self.managedObjectContext];
	
	
//	NSDictionary *stamp309 = [NSDictionary dictionaryWithObjectsAndKeys:
//							  @"Eat", @"stampType", 
//							  @"Mole", @"title", 
//							  [dateFormat dateFromString:@"2010-10-20"], @"dateStamped", 
//							  @"57 Jane St, NYC 10014", @"address", 
//							  @"Really reasonable and good mexican place in the village", @"message", 
//							  nil];
//	
//	[Stamp addStampWithId:[NSNumber numberWithInt:309] 
//				 fromUser:[NSNumber numberWithInt:3] 
//				 withData:stamp309
//   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp310 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Rye", @"title", 
							  [dateFormat dateFromString:@"2010-08-20"], @"dateStamped", 
							  @"247 South 1st St, NYC 11211", @"address", 
							  @"Meatloaf sandwich is amazing", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:310] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp310
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp311 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Iris Cafe", @"title", 
							  [dateFormat dateFromString:@"2011-01-02"], @"dateStamped", 
							  @"20 Columbia Place, NYC 11201", @"address", 
							  @"Breakfast baguette and pastries are so good", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:311] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp311
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp312 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Visit", @"stampType", 
							  @"Hotel Vitale", @"title", 
							  [dateFormat dateFromString:@"2011-01-24"], @"dateStamped", 
							  @"8 Mission St, San Francisco 94105", @"address", 
							  @"Great value in SF for a hotel", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:312] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp312
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp313 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Wear", @"stampType", 
							  @"J Crew Buttondown Shirts", @"title", 
							  [dateFormat dateFromString:@"2010-07-15"], @"dateStamped", 
							  @"Great value", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:313] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp313
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp314 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Wear", @"stampType", 
							  @"James Perse", @"title", 
							  [dateFormat dateFromString:@"2010-11-18"], @"dateStamped", 
							  @"Super soft clothing that is overpriced but worth it", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:314] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp314
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp315 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType", 
							  @"Palm Restaurant", @"title", 
							  [dateFormat dateFromString:@"2010-12-25"], @"dateStamped", 
							  @"94 Main St, East Hampton 11937", @"address", 
							  @"This is the best Palm. Chocolate cake is magical", @"message", 
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:315] 
				 fromUser:[NSNumber numberWithInt:3] 
				 withData:stamp315
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	
	
	
	
	
	
	//////// Kevin
	
	
	NSDictionary *stamp101 = [NSDictionary dictionaryWithObjectsAndKeys:
							 @"Drink", @"stampType", 
							 @"Employees Only", @"title", 
							 [dateFormat dateFromString:@"2010-01-28"], @"dateStamped", 
							 @"Bourbon, egg whites, and a bit of red wine, mixed with bitters and a touch of spice. Perfect winter drink.", @"message", 
							 nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:101] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp101
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp102 = [NSDictionary dictionaryWithObjectsAndKeys:
							 @"Wear", @"stampType", 
							 @"Patagonia Down Jacket", @"title", 
							 [dateFormat dateFromString:@"2010-12-25"], @"dateStamped", 
							 @"Got this from @Julia for Christmas... now I won't wear anything else.", @"message", 
							 @"http://www.patagonia.com/us/product/patagonia-mens-down-sweater-jacket?p=84673-0-616", @"urlWebsite",
							 nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:102] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp102
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp103 = [NSDictionary dictionaryWithObjectsAndKeys:
							 @"Watch", @"stampType", 
							 @"Lost in Translation", @"title", 
							 [dateFormat dateFromString:@"2010-09-14"], @"dateStamped", 
							 @"Still love it, and yet still can't get @Julia to stay awake for more than fifteen minutes.", @"message", 
							 @"http://www.imdb.com/title/tt0335266/", @"urlWebsite",
							 nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:103] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp103
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp104 = [NSDictionary dictionaryWithObjectsAndKeys:
							 @"Watch", @"stampType", 
							 @"The Merchant of Venice", @"title", 
							 [dateFormat dateFromString:@"2010-11-21"], @"dateStamped", 
							 @"Al Pacino was great, and the cast as a whole was amazing. It always surprises me how relevant Shakespeare can remain in modern times.", @"message", 
							 @"The Broadhurst Theater", @"address",
							 nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:104] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp104
   inManagedObjectContext:self.managedObjectContext];
	
	
	NSDictionary *stamp105 = [NSDictionary dictionaryWithObjectsAndKeys:
							 @"Listen", @"stampType", 
							 @"Lupe Fiasco - The Show Goes On", @"title", 
							 [dateFormat dateFromString:@"2010-12-08"], @"dateStamped", 
							 @"New single from Lupe!", @"message", 
							 @"http://itunes.apple.com/us/album/the-show-goes-on-single/id401085364", @"urlWebsite",
							 nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:105] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp105
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp106 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType",
							  @"Recette", @"title",
							  [dateFormat dateFromString:@"2011-01-22"], @"dateStamped",
							  @"328 West 12th St, New York 10014", @"address",
							  @"Unbelievable food. Get the five-course tasting, and make sure you get the pork belly with rock shrimp.", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:106] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp106
   inManagedObjectContext:self.managedObjectContext];

	
	NSDictionary *stamp107 = [NSDictionary dictionaryWithObjectsAndKeys:
							@"Read", @"stampType",
							@"When Genius Failed", @"title",
							[dateFormat dateFromString:@"2011-02-07"], @"dateStamped", 
							@"Really good book about LTCM and everything that went down. Scary parallels between this and what happened ten years later.", @"message",
							@"http://www.amazon.com/When-Genius-Failed-Long-Term-Management/dp/0375758259", @"urlWebsite",
							nil];	
	
	[Stamp addStampWithId:[NSNumber numberWithInt:107] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp107
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp108 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Buy", @"stampType",
							  @"MacBook Air", @"title",
							  [dateFormat dateFromString:@"2011-01-23"], @"dateStamped",
							  @"Incredibly fast and thin. Get the external monitor, too.", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:108] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp108
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp109 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType",
							  @"Shake Shack Double Shack Stack", @"title",
							  [dateFormat dateFromString:@"2010-09-23"], @"dateStamped",
							  @"@Tim check this out sometime. Doesn't look _that_ hard, right?", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:109] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp109
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp110 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Visit", @"stampType",
							  @"The James Hotel", @"title",
							  [dateFormat dateFromString:@"2010-12-04"], @"dateStamped",
							  @"My favorite hotel in the city, hands down. A bit far from the Loop but completely worth it.", @"message",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:110] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp110
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	NSDictionary *stamp111 = [NSDictionary dictionaryWithObjectsAndKeys:
							  @"Eat", @"stampType",
							  @"Avec", @"title",
							  [dateFormat dateFromString:@"2011-01-26"], @"dateStamped",
							  @"Chorizo-stuffed dates wrapped in bacon are still the best dish in Chicago. Can't recommend this place enough.", @"message",
							  @"615 W Randolph St, Chicago 60661", @"address",
							  nil];
	
	[Stamp addStampWithId:[NSNumber numberWithInt:111] 
				 fromUser:[NSNumber numberWithInt:1] 
				 withData:stamp111
   inManagedObjectContext:self.managedObjectContext];
	
	
	
	
	
	
	[dateFormat release];
	
	
	// Build Inbox and Load
	//InboxTableViewController *inboxvc = [[InboxTableViewController alloc] initInManagedObjectContext:self.managedObjectContext];
	InboxViewController *inboxvc = [[InboxViewController alloc] initInManagedObjectContext:self.managedObjectContext];
	
	UINavigationController *nav = [[UINavigationController alloc] init];
	[nav pushViewController:inboxvc animated:NO];
	[inboxvc release];
	
	
	
	
	
	
	[window addSubview:nav.view];
	[window	makeKeyAndVisible];
	
    return YES;
}


- (void)applicationWillResignActive:(UIApplication *)application {
    /*
     Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
     Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
     */
}


- (void)applicationDidEnterBackground:(UIApplication *)application {
    /*
     Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
     If your application supports background execution, called instead of applicationWillTerminate: when the user quits.
     */
    [self saveContext];
}


- (void)applicationWillEnterForeground:(UIApplication *)application {
    /*
     Called as part of the transition from the background to the inactive state: here you can undo many of the changes made on entering the background.
     */
}


- (void)applicationDidBecomeActive:(UIApplication *)application {
    /*
     Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
     */
}


/**
 applicationWillTerminate: saves changes in the application's managed object context before the application terminates.
 */
- (void)applicationWillTerminate:(UIApplication *)application {
    [self saveContext];
}


- (void)saveContext {
    
    NSError *error = nil;
	NSManagedObjectContext *managedObjectContext = self.managedObjectContext;
    if (managedObjectContext != nil) {
        if ([managedObjectContext hasChanges] && ![managedObjectContext save:&error]) {
            /*
             Replace this implementation with code to handle the error appropriately.
             
             abort() causes the application to generate a crash log and terminate. You should not use this function in a shipping application, although it may be useful during development. If it is not possible to recover from the error, display an alert panel that instructs the user to quit the application by pressing the Home button.
             */
            NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
            abort();
        } 
    }
}    


#pragma mark -
#pragma mark Core Data stack

/**
 Returns the managed object context for the application.
 If the context doesn't already exist, it is created and bound to the persistent store coordinator for the application.
 */
- (NSManagedObjectContext *)managedObjectContext {
    
    if (managedObjectContext_ != nil) {
        return managedObjectContext_;
    }
    
    NSPersistentStoreCoordinator *coordinator = [self persistentStoreCoordinator];
    if (coordinator != nil) {
        managedObjectContext_ = [[NSManagedObjectContext alloc] init];
        [managedObjectContext_ setPersistentStoreCoordinator:coordinator];
    }
    return managedObjectContext_;
}


/**
 Returns the managed object model for the application.
 If the model doesn't already exist, it is created from the application's model.
 */
- (NSManagedObjectModel *)managedObjectModel {
    
    if (managedObjectModel_ != nil) {
        return managedObjectModel_;
    }
    NSURL *modelURL = [[NSBundle mainBundle] URLForResource:@"Stamped" withExtension:@"momd"];
    managedObjectModel_ = [[NSManagedObjectModel alloc] initWithContentsOfURL:modelURL];    
    return managedObjectModel_;
}


/**
 Returns the persistent store coordinator for the application.
 If the coordinator doesn't already exist, it is created and the application's store added to it.
 */
- (NSPersistentStoreCoordinator *)persistentStoreCoordinator {
    
    if (persistentStoreCoordinator_ != nil) {
        return persistentStoreCoordinator_;
    }
    
    NSURL *storeURL = [[self applicationDocumentsDirectory] URLByAppendingPathComponent:@"Stamped.sqlite"];
    
    NSError *error = nil;
    persistentStoreCoordinator_ = [[NSPersistentStoreCoordinator alloc] initWithManagedObjectModel:[self managedObjectModel]];
    if (![persistentStoreCoordinator_ addPersistentStoreWithType:NSSQLiteStoreType configuration:nil URL:storeURL options:nil error:&error]) {
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
         [NSDictionary dictionaryWithObjectsAndKeys:[NSNumber numberWithBool:YES],NSMigratePersistentStoresAutomaticallyOption, [NSNumber numberWithBool:YES], NSInferMappingModelAutomaticallyOption, nil];
         
         Lightweight migration will only work for a limited set of schema changes; consult "Core Data Model Versioning and Data Migration Programming Guide" for details.
         
         */
        NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
        abort();
    }    
    
    return persistentStoreCoordinator_;
}


#pragma mark -
#pragma mark Application's Documents directory

/**
 Returns the URL to the application's Documents directory.
 */
- (NSURL *)applicationDocumentsDirectory {
    return [[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask] lastObject];
}


#pragma mark -
#pragma mark Memory management

- (void)applicationDidReceiveMemoryWarning:(UIApplication *)application {
    /*
     Free up as much memory as possible by purging cached data objects that can be recreated (or reloaded from disk) later.
     */
}


- (void)dealloc {
    
    [managedObjectContext_ release];
    [managedObjectModel_ release];
    [persistentStoreCoordinator_ release];
    
    [window release];
    [super dealloc];
}


@end

