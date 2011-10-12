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
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "TodoTableViewCell.h"
#import "User.h"
#import "Util.h"
#import "Stamp.h"

static NSString* const kShowFavoritesPath = @"/favorites/show.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";

@interface TodoViewController ()
- (void)loadFavoritesFromDataStore;
- (void)loadFavoritesFromNetwork;
- (void)favoriteDidChange:(NSNotification*)notification;
- (void)removeFavoriteWithEntityID:(NSString*)entityID;

@property (nonatomic, copy) NSArray* favoritesArray;
@end

@implementation TodoViewController

@synthesize favoritesArray = favoritesArray_;
@synthesize delegate = delegate_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.favoritesArray = nil;
  self.delegate = nil;
  [super dealloc];
}

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
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.favoritesArray = nil;
  self.delegate = nil;
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
  if (favoritesArray_ != nil)
    return self.favoritesArray.count + 1;  // One more for adding friends.
  
  return 0;
}

- (float)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.row == 0)
    return 50.0;
  else 
    return 82.0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0 && favoritesArray_ != nil) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                                    reuseIdentifier:nil] autorelease];
    UIImageView* addFriendsImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"button_addTodo"]];
    addFriendsImageView.center = cell.contentView.center;
    addFriendsImageView.frame = CGRectOffset(addFriendsImageView.frame, 0.0, 4.0);
    [cell addSubview:addFriendsImageView];
    [addFriendsImageView release];
    return cell;
  }

  
  static NSString* CellIdentifier = @"Cell";

  TodoTableViewCell* cell = (TodoTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[TodoTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  Favorite* fave = [self.favoritesArray objectAtIndex:indexPath.row - 1];
  cell.delegate = self;
  cell.favorite = fave;
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    [self.delegate displaySearchEntities];
    return;
  }
  
  Favorite* fave = [self.favoritesArray objectAtIndex:indexPath.row - 1];
  UIViewController* detailViewController = [Util detailViewControllerForEntity:fave.entityObject];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
}

//-(void)tableView:(UITableView*)tableView willBeginEditingRowAtIndexPath:(NSIndexPath *)indexPath {
//  TodoTableViewCell* cell = (TodoTableViewCell*)[self tableView:tableView cellForRowAtIndexPath:indexPath];
//}


//-(void)tableView:(UITableView *)tableView didEndEditingRowAtIndexPath:(NSIndexPath *)indexPath {
//  TodoTableViewCell* cell = (TodoTableViewCell*)[self tableView:tableView cellForRowAtIndexPath:indexPath];
//}

-(BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.row == 0) 
    return NO;
  return YES;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle 
forRowAtIndexPath:(NSIndexPath *)indexPath {
  // If row is deleted, remove it from the list.
  if (editingStyle == UITableViewCellEditingStyleDelete) {
    Favorite* fave = [self.favoritesArray objectAtIndex:indexPath.row - 1];
    [self removeFavoriteWithEntityID:fave.entityObject.entityID];
    
    fave.entityObject = nil;
    fave.stamp.isFavorited = NO;
    [fave.managedObjectContext save:nil];


    NSMutableArray* tempFaves = self.favoritesArray.mutableCopy;
    [tempFaves removeObjectAtIndex:indexPath.row - 1];
    self.favoritesArray = tempFaves;
    
    [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationMiddle];
  }
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

  NSArray* toDelete = [Favorite objectsWithPredicate:[NSPredicate predicateWithFormat:@"entityObject == NIL"]];
  for (Favorite* fave in toDelete)
    [fave.managedObjectContext deleteObject:fave];

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

- (void)removeFavoriteWithEntityID:(NSString*)entityID {
  NSString* path = kRemoveFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:entityID, @"entity_id", nil];

  [objectLoader send];
}


@end
