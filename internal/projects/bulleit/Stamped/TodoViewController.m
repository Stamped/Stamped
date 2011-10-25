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
- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath;
- (void)removeFavoriteWithEntityID:(NSString*)entityID;

@property (nonatomic, retain) NSFetchedResultsController* fetchedResultsController;
@end

@implementation TodoViewController

@synthesize delegate = delegate_;
@synthesize fetchedResultsController = fetchedResultsController_;

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.delegate = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
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
  [self loadFavoritesFromDataStore];
  [self loadFavoritesFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.delegate = nil;
  self.fetchedResultsController.delegate = nil;
  self.fetchedResultsController = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  NSArray* toDelete = [Favorite objectsWithPredicate:[NSPredicate predicateWithFormat:@"entityObject == NIL"]];
  for (Favorite* fave in toDelete)
    [Favorite.managedObjectContext deleteObject:fave];
}

- (void)configureCell:(UITableViewCell*)cell atIndexPath:(NSIndexPath*)indexPath {
  Favorite* fave = [fetchedResultsController_ objectAtIndexPath:indexPath];
  [(TodoTableViewCell*)cell setDelegate:self];
  [(TodoTableViewCell*)cell setFavorite:fave];
}

#pragma mark - NSFetchedResultsControllerDelegate methods.

- (void)controllerWillChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView beginUpdates];
}

- (void)controller:(NSFetchedResultsController*)controller 
   didChangeObject:(id)anObject
       atIndexPath:(NSIndexPath*)indexPath
     forChangeType:(NSFetchedResultsChangeType)type
      newIndexPath:(NSIndexPath*)newIndexPath {  
  indexPath = [NSIndexPath indexPathForRow:(indexPath.row + 1) inSection:0];
  newIndexPath = [NSIndexPath indexPathForRow:(newIndexPath.row + 1) inSection:0];

  UITableView* tableView = self.tableView;
  
  switch(type) {
    case NSFetchedResultsChangeInsert:
      [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath] withRowAnimation:UITableViewRowAnimationNone];
      break;
      
    case NSFetchedResultsChangeDelete:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
      break;
      
    case NSFetchedResultsChangeUpdate:
      [self configureCell:[tableView cellForRowAtIndexPath:indexPath] atIndexPath:indexPath];
      break;
      
    case NSFetchedResultsChangeMove:
      [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
      [tableView reloadSections:[NSIndexSet indexSetWithIndex:newIndexPath.section] withRowAnimation:UITableViewRowAnimationNone];
      break;
  }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController*)controller {
  [self.tableView endUpdates];
}

#pragma mark - Table view data source

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  id<NSFetchedResultsSectionInfo> sectionInfo = [[fetchedResultsController_ sections] objectAtIndex:section];
  return [sectionInfo numberOfObjects] + 1;
}

- (float)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0)
    return 50.0;
  else 
    return 82.0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                                    reuseIdentifier:nil] autorelease];
    UIImageView* addTodoImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"button_addTodo"]];
    addTodoImageView.center = cell.contentView.center;
    addTodoImageView.frame = CGRectOffset(addTodoImageView.frame, 0.0, 4.0);
    [cell addSubview:addTodoImageView];
    [addTodoImageView release];
    return cell;
  }

  static NSString* CellIdentifier = @"Cell";

  TodoTableViewCell* cell = (TodoTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[TodoTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
  [self configureCell:cell atIndexPath:offsetIndexPath];

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    [self.delegate displaySearchEntities];
    return;
  }

  NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
  Favorite* fave = [fetchedResultsController_ objectAtIndexPath:offsetIndexPath];
  UIViewController* detailViewController = [Util detailViewControllerForEntity:fave.entityObject];
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
}

- (BOOL)tableView:(UITableView*)tableView canEditRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) 
    return NO;

  return YES;
}

- (void)tableView:(UITableView*)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath*)indexPath {
  // If row is deleted, remove it from the list.
  if (editingStyle == UITableViewCellEditingStyleDelete) {
    NSIndexPath* offsetIndexPath = [NSIndexPath indexPathForRow:(indexPath.row - 1) inSection:0];
    Favorite* fave = [fetchedResultsController_ objectAtIndexPath:offsetIndexPath];

    NSString* entityID = fave.entityObject.entityID;
    fave.entityObject.favorite = nil;
    fave.entityObject = nil;
    fave.stamp.isFavorited = [NSNumber numberWithBool:NO];
    [Favorite.managedObjectContext deleteObject:fave];
    
    [self removeFavoriteWithEntityID:entityID];    
  }
}


#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
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
  [self setIsLoading:YES];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kShowFavoritesPath
                                                                    delegate:self];
  objectLoader.objectMapping = favoriteMapping;
  [objectLoader send];
}

- (void)loadFavoritesFromDataStore {
  if (!fetchedResultsController_) {
    NSFetchRequest* request = [Favorite fetchRequest];
    NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
    [request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
    User* user = [AccountManager sharedManager].currentUser;
    [request setPredicate:[NSPredicate predicateWithFormat:@"userID == %@ AND entityObject != NIL", user.userID]];
    NSFetchedResultsController* fetchedResultsController =
        [[NSFetchedResultsController alloc] initWithFetchRequest:request
                                            managedObjectContext:[Favorite managedObjectContext]
                                              sectionNameKeyPath:nil
                                                       cacheName:@"FavoriteItems"];
    self.fetchedResultsController = fetchedResultsController;
    fetchedResultsController.delegate = self;
    [fetchedResultsController release];
  }
  
  NSError* error;
	if (![self.fetchedResultsController performFetch:&error]) {
		// Update to handle the error appropriately.
		NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
	}
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
