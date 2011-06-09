    //
//  InboxViewController.m
//  Stamped
//
//  Created by Kevin Palms on 2/8/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "InboxViewController.h"
#import "CoreDataTableViewController.h"
#import "Stamp.h"
#import "User.h"
#import "StampDetailViewController.h"

@interface InboxViewController()
@property (retain) NSManagedObjectContext *managedObjectContext;
@property (retain) UISegmentedControl *segmentedControl;
@property NSInteger activeSegmentedControl;
@end


@implementation InboxViewController

@synthesize managedObjectContext, segmentedControl, activeSegmentedControl, fetchedResultsController;

// MARK: -
// MARK: Initialization

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context
{
    if (self = [super init]) {
		self.managedObjectContext = context;
    }
    return self;
}


- (void)viewWillAppear:(BOOL)animated
{
//	NSLog(@"View Will Appear!");
	
	// TODO: Make this default behavior, only load frc on first time?
	if (self.fetchedResultsController) {
		[inboxTableView reloadData];
		return;
	}
	
	self.title = @"Inbox";
	
	UIBarButtonItem *newStamp = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemCompose 
																			  target:self 
																			  action:@selector(alertNewStamp)];
	self.navigationItem.rightBarButtonItem = newStamp;
	[newStamp release];
	
	UIImage *navButtonImage = nil;
	if ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2)
	{
		// Retina
		navButtonImage = [UIImage imageWithCGImage:[[UIImage imageNamed:@"squares-2x.png"] CGImage] 
											 scale:2.0 
									   orientation:UIImageOrientationUp];
	} else {
		// Normal
		navButtonImage = [UIImage imageWithCGImage:[[UIImage imageNamed:@"squares.png"] CGImage] 
											 scale:1.0 
									   orientation:UIImageOrientationUp];
	}
	UIBarButtonItem *navButton = [[UIBarButtonItem alloc] initWithImage:navButtonImage
																  style:UIBarButtonItemStyleBordered 
																 target:self 
																 action:@selector(alertNav)];
	navButton.width = 78;
	
	self.navigationItem.leftBarButtonItem = navButton;
	[navButton release];
	
	
//	UIImage *faceImage = [UIImage imageNamed:@"squares-2x.png"];
//	
//	faceImage.size.width = 20;
//	faceImage.size.height = 20;
//	
//	UIButton *face = [UIButton buttonWithType:UIBarButtonItemStyleBordered];
//	
//	face.bounds = CGRectMake( 0, 0, 20, 20 );
//	
//	[face setImage:faceImage forState:UIControlStateNormal];
//	
//	UIBarButtonItem *faceBtn = [[UIBarButtonItem alloc] initWithCustomView:face];
//	
//	self.navigationItem.leftBarButtonItem = faceBtn;
//	[faceBtn release];
	
	
	
	UIView *inboxView = [[UIView alloc] initWithFrame:CGRectMake(0, 
																 0, 
																 [[UIScreen mainScreen] applicationFrame].size.width, 
																 [[UIScreen mainScreen] applicationFrame].size.height)];
	
	self.inboxTableView = [[UITableView alloc] initWithFrame:CGRectMake(0, 
																		0, 
																		[[UIScreen mainScreen] applicationFrame].size.width, 
																		[[UIScreen mainScreen] applicationFrame].size.height - 88)];
	
	[inboxView addSubview:inboxTableView];
//	[inboxTableView release];
	

	// Toolbar
	UIToolbar *inboxToolbar = [UIToolbar new];
	inboxToolbar.barStyle = UIBarStyleDefault;
	[inboxToolbar setFrame:CGRectMake(0, // x-axis
								 [[UIScreen mainScreen] applicationFrame].size.height - 88, // y-axis
								 [[UIScreen mainScreen] applicationFrame].size.width, // width
								 44)]; // height
	
	NSArray *toolbarActions = [NSArray arrayWithObjects:@"Starred", @"All", @"Filter", nil];
	
	if (!segmentedControl) segmentedControl = [[UISegmentedControl alloc] initWithItems:toolbarActions];
	segmentedControl.frame = CGRectMake(35, 7, 250, 30);
	segmentedControl.segmentedControlStyle = UISegmentedControlStyleBar;
	
	[segmentedControl addTarget:self action:@selector(selectSegmentedControl:) forControlEvents:UIControlEventValueChanged];
	
	segmentedControl.selectedSegmentIndex = 1;
	
	[inboxToolbar addSubview:segmentedControl];
	
	[inboxView addSubview:inboxToolbar];
	[inboxToolbar release];
	
	self.view = inboxView;
	[inboxView release];
}


- (void)applyFilterForPredicate:(NSPredicate *)filterPredicate withCacheName:(NSString *)cacheName
{	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"Stamp" inManagedObjectContext:managedObjectContext];
	fetchRequest.sortDescriptors = [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"dateStamped" 
																						   ascending:NO
																							selector:@selector(compare:)]];
	fetchRequest.predicate = filterPredicate;
	
	NSFetchedResultsController *frc = [[NSFetchedResultsController alloc]
										initWithFetchRequest:fetchRequest
										managedObjectContext:managedObjectContext 
										sectionNameKeyPath:nil 
										cacheName:cacheName];
	[fetchRequest release];
	
	self.fetchedResultsController = frc;
	[frc release];
}


- (void)selectSegmentedControl:(UISegmentedControl *)aSegmentedControl
{	
	if (aSegmentedControl.selectedSegmentIndex != activeSegmentedControl || 
		aSegmentedControl.selectedSegmentIndex == 2) 
	{
		switch (aSegmentedControl.selectedSegmentIndex) {
				
			case 0:
				// Starred
				[self applyFilterForPredicate:[NSPredicate predicateWithFormat:@"isStarred = YES"] withCacheName:@"inboxStarred"];
				self.title = @"Inbox (Starred)";
				activeSegmentedControl = aSegmentedControl.selectedSegmentIndex;
				
				break;
				
			case 1:
				// All
				[self applyFilterForPredicate:nil withCacheName:@"inboxAll"];
				self.title = @"Inbox";
				activeSegmentedControl = aSegmentedControl.selectedSegmentIndex;
				
				break;
				
			case 2:
				// Filter
				; // Necessary for some reason, or else it fails.. very strange
				FilterViewController *fvc = [[FilterViewController alloc] initInManagedObjectContext:self.managedObjectContext];
				fvc.delegate = self;
				
				UINavigationController *nc = [[UINavigationController alloc] initWithRootViewController:fvc];
				[self presentModalViewController:nc animated:YES];
				
				[nc release];
				[fvc release];
				
				break;
		}
		
	}
}

- (void) alertNav
{
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"DEMO" 
													 message:@"[Navigation Screen]" 
													delegate:self 
										   cancelButtonTitle:@"Cancel" 
										   otherButtonTitles:nil] autorelease];
    [alert show];
}

- (void) alertNewStamp
{
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"DEMO" 
													 message:@"[Add New Stamp]" 
													delegate:self 
										   cancelButtonTitle:@"Cancel" 
										   otherButtonTitles:nil] autorelease];
    [alert show];
}
	


// MARK: -
// MARK: InboxTableView

- (UITableView *)inboxTableView
{
	return inboxTableView;
}

- (void)setInboxTableView:(UITableView *)newInboxTableView
{
	[inboxTableView release];
	inboxTableView = [newInboxTableView retain];
	[inboxTableView setDelegate:self];
	[inboxTableView setDataSource:self];
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return 88;
}



// MARK: -
// MARK: Core Data

- (void)performFetchForTableView:(UITableView *)tableView
{
	NSError *error = nil;
	[self.fetchedResultsController performFetch:&error];
	if (error) {
		NSLog(@"[CoreDataTableViewController performFetchForTableView:] %@ (%@)", [error localizedDescription], [error localizedFailureReason]);
	}
	[tableView reloadData];
}

- (void)setFetchedResultsController:(NSFetchedResultsController *)controller
{
	fetchedResultsController.delegate = nil;
	[fetchedResultsController release];
	fetchedResultsController = [controller retain];
	controller.delegate = self;
	normalPredicate = [self.fetchedResultsController.fetchRequest.predicate retain];
	/*if (self.view.window)*/ [self performFetchForTableView:self.inboxTableView];
}

- (NSFetchedResultsController *)fetchedResultsControllerForTableView:(UITableView *)tableView
{
	if (tableView == self.inboxTableView) {
		if (self.fetchedResultsController.fetchRequest.predicate != normalPredicate) {
			NSLog(@"Run something");
			[NSFetchedResultsController deleteCacheWithName:self.fetchedResultsController.cacheName];
			self.fetchedResultsController.fetchRequest.predicate = normalPredicate;
			[self performFetchForTableView:tableView];
		}
	}
	return self.fetchedResultsController;
}


// MARK: UITableViewDataSource methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[[self fetchedResultsControllerForTableView:tableView] sections] count];
}

- (NSArray *)sectionIndexTitlesForTableView:(UITableView *)tableView
{
	return [[self fetchedResultsControllerForTableView:tableView] sectionIndexTitles];
}

// MARK: UITableViewDelegate methods

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [[[[self fetchedResultsControllerForTableView:tableView] sections] objectAtIndex:section] numberOfObjects];
}

// MARK: FilterViewDelegate methods

- (void)applyFilterOnStampType:(NSString *)stampType
{	
	// TODO: Add "enum" so they can only pick from a certain subset of strings
	
	[self applyFilterForPredicate:[NSPredicate predicateWithFormat:@"stampType = %@" argumentArray:[NSArray arrayWithObject:stampType]] 
					withCacheName:[NSString stringWithFormat:@"%@All", stampType]];
	
	self.title = [NSString stringWithFormat:@"Inbox (%@)", stampType];
	
	activeSegmentedControl = -1;
	[segmentedControl removeTarget:self action:@selector(selectSegmentedControl:) forControlEvents:UIControlEventValueChanged];
	self.segmentedControl.selectedSegmentIndex = -1;
	[segmentedControl addTarget:self action:@selector(selectSegmentedControl:) forControlEvents:UIControlEventValueChanged];
	
	[self dismissModalViewControllerAnimated:YES];
}

- (IBAction)dismissModal:(id)sender {
	self.segmentedControl.selectedSegmentIndex = activeSegmentedControl;
	[self dismissModalViewControllerAnimated:YES];
}




// MARK: -
// MARK: TableView

- (UITableViewCell *)tableView:(UITableView *)tableView cellForManagedObject:(NSManagedObject *)managedObject
{
    static NSString *ReuseIdentifier = @"CoreDataTableViewCell";
    
    StampCell *cell = (StampCell *)[tableView dequeueReusableCellWithIdentifier:ReuseIdentifier];
    if (cell == nil) {
		UITableViewCellStyle cellStyle = UITableViewCellStyleDefault;
        cell = [[[StampCell alloc] initWithStyle:cellStyle reuseIdentifier:ReuseIdentifier] autorelease];
    }
	
	Stamp *stamp = (Stamp *)managedObject;
	User *user = [User userWithId:stamp.userId inManagedObjectContext:self.managedObjectContext];
	
	cell.accessoryType = UITableViewCellAccessoryNone;
	
	cell.stampCellType.text		= stamp.stampType;
	cell.stampCellTitle.text	= stamp.title;
	cell.stampCellUsers.text	= user.name;
	cell.stampCellImage.image	= [StampCell imageThumbnailForStampId:stamp.stampId];
	cell.stampCellDate.text		= [StampCell timestampFromDateStamped:stamp.dateStamped];
	
	return cell;
}

- (UIImage *)thumbnailImageForManagedObject:(NSManagedObject *)managedObject 
{
	Stamp *stamp = (Stamp *)managedObject;
	
	NSString *thumbnail = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) 
						? [NSString stringWithFormat:@"e-%@-2x", stamp.stampId] 
						: [NSString stringWithFormat:@"e-%@", stamp.stampId];
	
	if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]]) {
		return [UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]];
	}
	
	return nil;
}


- (void)managedObjectSelected:(NSManagedObject *)managedObject
{
	Stamp *stamp = (Stamp *)managedObject;
	
	StampDetailViewController *sdvc = [[StampDetailViewController alloc] initInManagedObjectContext:stamp.managedObjectContext];
	sdvc.stampId = stamp.stampId;
	sdvc.title = stamp.title;
	
	[self.navigationController pushViewController:sdvc animated:YES];
	[sdvc release];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{    
	return [self tableView:tableView cellForManagedObject:[[self fetchedResultsControllerForTableView:tableView] objectAtIndexPath:indexPath]];
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[self managedObjectSelected:[[self fetchedResultsControllerForTableView:tableView] objectAtIndexPath:indexPath]];
}



//- (NSInteger)numberOfSectionsInTableView:(UITableView *)inboxTableView
//{
//	return 1;
//}
//
//- (NSInteger)tableView:(UITableView *)inboxTableView numberOfRowsInSection:(NSInteger)section
//{
//	return 12;
//}

//- (void)updateWithDateComponents:(NSDateComponents *)components
//{
//	[inboxTableView reloadData];
//}

//- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
//{
//	static NSString *cellId = @"Cell";
//	
//	UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:cellId];
//	if (cell == nil)
//	{
//		cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:cellId] autorelease];
//	}
//	
////	NSString *componentName = @"Random String";
//	cell.textLabel.text = @"Random Cell";
//	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
//	
//	return cell;
//}
//
//- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
//{
////	Stamp *stamp = (Stamp *)managedObject;
//	
//	StampDetailViewController *sdvc = [[StampDetailViewController alloc] initInManagedObjectContext:self.managedObjectContext];
//	sdvc.stampId = [NSNumber numberWithInt:1];
//	sdvc.title = @"New Object";
//	
//	[self.navigationController pushViewController:sdvc animated:YES];
//	[sdvc release];
//}



/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView {
}
*/

/*
// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
    [super viewDidLoad];
}
*/

/*
// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations.
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}
*/

// MARK: -
// MARK: Unloading

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
}

- (void)viewDidUnload {
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}


- (void)dealloc {
	[segmentedControl release];
	[inboxTableView release];
	[normalPredicate release];
	[fetchedResultsController release];
    [super dealloc];
}


@end


