//
//  InboxAViewController.m
//  StampedMockB
//
//  Created by Kevin Palms on 6/27/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "InboxAViewController.h"
#import "CoreDataTableViewController.h"
#import "Stamp.h"
#import "DetailAViewController.h"

@interface InboxAViewController()
@property (retain) NSManagedObjectContext *managedObjectContext;
@end

@implementation InboxAViewController

@synthesize managedObjectContext, fetchedResultsController;

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context
{
  self = [super init];
  if (self) {
    self.managedObjectContext = context;
  }
  return self;
}

- (void)dealloc
{
  [inboxTableView release];
  [fetchedResultsController release];
  [normalPredicate release];
  [super dealloc];
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle


// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)viewWillAppear:(BOOL)animated
{
  if (self.fetchedResultsController) {
		[inboxTableView reloadData];
		return;
	}
  
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"Stamp" inManagedObjectContext:managedObjectContext];
	fetchRequest.sortDescriptors = [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"timestamp" 
                                                                                        ascending:NO
                                                                                         selector:@selector(compare:)]];
	
	NSFetchedResultsController *frc = [[NSFetchedResultsController alloc]
                                     initWithFetchRequest:fetchRequest
                                     managedObjectContext:managedObjectContext 
                                     sectionNameKeyPath:nil 
                                     cacheName:@"inboxAll"];
	[fetchRequest release];
	
	self.fetchedResultsController = frc;
  
  
  self.title = @"Stamped";
  
  UIView *inboxView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, [[UIScreen mainScreen] applicationFrame].size.width, [[UIScreen mainScreen] applicationFrame].size.height - 44)];
  self.inboxTableView = [[UITableView alloc] initWithFrame:inboxView.frame];
  [inboxView addSubview:inboxTableView];
  
  self.view = inboxView;
  [inboxView release];
}


/*
// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    [super viewDidLoad];
}
*/


// MARK: -
// MARK: InboxTableView

////////////////////////////////////////////////////////////////////////////////
- (UITableView *)inboxTableView
{
	return inboxTableView;
}

////////////////////////////////////////////////////////////////////////////////
- (void)setInboxTableView:(UITableView *)newInboxTableView
{
	[inboxTableView release];
	inboxTableView = [newInboxTableView retain];
	[inboxTableView setDelegate:self];
	[inboxTableView setDataSource:self];
}

////////////////////////////////////////////////////////////////////////////////
- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return 84;
}

// MARK: -
// MARK: Core Data

////////////////////////////////////////////////////////////////////////////////
- (void)performFetchForTableView:(UITableView *)tableView
{
	NSError *error = nil;
	[self.fetchedResultsController performFetch:&error];
	if (error) {
		NSLog(@"[CoreDataTableViewController performFetchForTableView:] %@ (%@)", [error localizedDescription], [error localizedFailureReason]);
	}
	[tableView reloadData];
}

////////////////////////////////////////////////////////////////////////////////
- (void)setFetchedResultsController:(NSFetchedResultsController *)controller
{
	fetchedResultsController.delegate = nil;
	[fetchedResultsController release];
	fetchedResultsController = [controller retain];
	controller.delegate = self;
	normalPredicate = [self.fetchedResultsController.fetchRequest.predicate retain];
	[self performFetchForTableView:self.inboxTableView];
}

////////////////////////////////////////////////////////////////////////////////
- (NSFetchedResultsController *)fetchedResultsControllerForTableView:(UITableView *)tableView
{
	if (tableView == self.inboxTableView) {
		if (self.fetchedResultsController.fetchRequest.predicate != normalPredicate) {
			[NSFetchedResultsController deleteCacheWithName:self.fetchedResultsController.cacheName];
			self.fetchedResultsController.fetchRequest.predicate = normalPredicate;
			[self performFetchForTableView:tableView];
		}
	}
	return self.fetchedResultsController;
}


// MARK: UITableViewDataSource methods

////////////////////////////////////////////////////////////////////////////////
- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
  return [[[self fetchedResultsControllerForTableView:tableView] sections] count];
}

////////////////////////////////////////////////////////////////////////////////
- (NSArray *)sectionIndexTitlesForTableView:(UITableView *)tableView
{
	return [[self fetchedResultsControllerForTableView:tableView] sectionIndexTitles];
}


// MARK: UITableViewDelegate methods

////////////////////////////////////////////////////////////////////////////////
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
  return [[[[self fetchedResultsControllerForTableView:tableView] sections] objectAtIndex:section] numberOfObjects];
}


// MARK: -
// MARK: TableView

////////////////////////////////////////////////////////////////////////////////
- (UITableViewCell *)tableView:(UITableView *)tableView cellForManagedObject:(NSManagedObject *)managedObject
{
  static NSString *ReuseIdentifier = @"CoreDataTableViewCell";
  
  InboxACell *cell = (InboxACell *)[tableView dequeueReusableCellWithIdentifier:ReuseIdentifier];
  if (cell == nil) {
		UITableViewCellStyle cellStyle = UITableViewCellStyleDefault;
    cell = [[[InboxACell alloc] initWithStyle:cellStyle reuseIdentifier:ReuseIdentifier] autorelease];
  }
	
	Stamp *stamp = (Stamp *)managedObject;
	//User *user = [User userWithId:stamp.userId inManagedObjectContext:self.managedObjectContext];
	
	cell.accessoryType = UITableViewCellAccessoryNone;
	
	cell.cellTitle.text         = stamp.title;
	cell.cellSubtitle.text      = stamp.comment;
  cell.cellAvatar.image       = [UIImage imageNamed:[NSString stringWithFormat:@"user-image-%@.png", stamp.avatar]];
  cell.cellStamp.image        = [UIImage imageNamed:[NSString stringWithFormat:@"user-stamp-%@.png", stamp.stampImage]];
  [cell formatStamp];
  
  [cell showPhotoTag:[stamp.hasPhoto boolValue]];
//	cell.stampCellTitle.text	= stamp.title;
//	cell.stampCellUsers.text	= user.name;
//	cell.stampCellImage.image	= [StampCell imageThumbnailForStampId:stamp.stampId];
//	cell.stampCellDate.text		= [StampCell timestampFromDateStamped:stamp.dateStamped];
	
	return cell;
}

////////////////////////////////////////////////////////////////////////////////
- (UIImage *)thumbnailImageForManagedObject:(NSManagedObject *)managedObject 
{
	//Stamp *stamp = (Stamp *)managedObject;
	
//	NSString *thumbnail = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) 
//  ? [NSString stringWithFormat:@"e-%@-2x", stamp.stampId] 
//  : [NSString stringWithFormat:@"e-%@", stamp.stampId];
  NSString *thumbnail = @"e-1-2x"; // TEMP
	
	if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]]) {
		return [UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]];
	}
	
	return nil;
}

////////////////////////////////////////////////////////////////////////////////
- (void)managedObjectSelected:(NSManagedObject *)managedObject
{
	Stamp *stamp = (Stamp *)managedObject;
	
	DetailAViewController *sdvc = [[DetailAViewController alloc] initInManagedObjectContext:stamp.managedObjectContext];
	//sdvc.stampID = stamp.stampId;
  sdvc.stampID = [stamp objectID];
	sdvc.title = stamp.title;
	
	[self.navigationController pushViewController:sdvc animated:YES];
	[sdvc release];
}

////////////////////////////////////////////////////////////////////////////////
- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{    
	return [self tableView:tableView 
    cellForManagedObject:[[self fetchedResultsControllerForTableView:tableView] objectAtIndexPath:indexPath]];
}

////////////////////////////////////////////////////////////////////////////////
- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[self managedObjectSelected:[[self fetchedResultsControllerForTableView:tableView] objectAtIndexPath:indexPath]];
}


// MARK: -
// MARK: Unload

////////////////////////////////////////////////////////////////////////////////
- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

@end
