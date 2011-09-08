//
//  TodoViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/19/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "TodoViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Favorite.h"
#import "Notifications.h"
#import "PlaceDetailViewController.h"
#import "GenericItemDetailViewController.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "TodoTableViewCell.h"
#import "User.h"

static NSString* const kShowFavoritesPath = @"/favorites/show.json";

@interface TodoViewController ()
- (void)loadFavoritesFromDataStore;
- (void)loadFavoritesFromNetwork;
- (void)favoriteDidChange:(NSNotification*)notification;

@property (nonatomic, copy) NSArray* favoritesArray;
@end

@implementation TodoViewController

@synthesize favoritesArray = favoritesArray_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)userPulledToReload {
  [self loadFavoritesFromNetwork];
}

- (void)reloadData {
  // Reload the view if needed.
  [self view];
  [self loadFavoritesFromNetwork];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self 
                                           selector:@selector(favoriteDidChange:) 
                                               name:kFavoriteHasChangedNotification 
                                             object:nil];
  [self loadFavoritesFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.favoritesArray = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self loadFavoritesFromDataStore];
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return self.favoritesArray.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";

  TodoTableViewCell* cell = (TodoTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[TodoTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  Favorite* fave = [self.favoritesArray objectAtIndex:indexPath.row];
  cell.delegate = self;
  cell.favorite = fave;
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Favorite* fave = [self.favoritesArray objectAtIndex:indexPath.row];
  EntityDetailViewController* detailViewController = nil;
  switch (fave.entityObject.entityCategory) {
    case EntityCategoryFood:
      detailViewController = [[PlaceDetailViewController alloc] initWithEntityObject:fave.entityObject];
      break;
    default:
      detailViewController = [[GenericItemDetailViewController alloc] initWithEntityObject:fave.entityObject];
      break;
  }

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[self loadFavoritesFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  [self loadFavoritesFromDataStore];
} 

#pragma mark - TodoTableViewCellDelegate Methods.

- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldStampEntity:(Entity*)entity {
  CreateStampViewController* detailViewController = [[CreateStampViewController alloc] initWithEntityObject:entity];
  
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldShowStamp:(Stamp*)stamp {
  if (!stamp)
    return;
  
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - Custom methods.

- (void)loadFavoritesFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kShowFavoritesPath
                                                                    delegate:self];
  objectLoader.objectMapping = favoriteMapping;
  [objectLoader send];
}

- (void)loadFavoritesFromDataStore {
  self.favoritesArray = nil;
  NSFetchRequest* request = [Favorite fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  User* user = [AccountManager sharedManager].currentUser;
  [request setPredicate:[NSPredicate predicateWithFormat:@"userID == %@", user.userID]];
	self.favoritesArray = [Favorite objectsWithFetchRequest:request];
  [self.tableView reloadData];
  self.tableView.contentOffset = scrollPosition_;
}

- (void)favoriteDidChange:(NSNotification*)notification {
  [self loadFavoritesFromDataStore];
}

@end
