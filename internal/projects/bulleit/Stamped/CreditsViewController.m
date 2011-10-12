//
//  CreditsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreditsViewController.h"

#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreditTableViewCell.h"
#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"

static NSString* const kCreditsPath = @"/collections/credit.json";

@interface CreditsViewController ()
- (void)loadStampsFromNetwork;

@property (nonatomic, copy) NSArray* stampsArray;
@end

@implementation CreditsViewController

@synthesize tableView = tableView_;
@synthesize stampsArray = stampsArray_;
@synthesize screenName = screenName_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  
  self.tableView = nil;
  self.stampsArray = nil;
  self.screenName = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.tableView = nil;
  self.stampsArray = nil;
  self.screenName = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
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

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return stampsArray_.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";
  
  CreditTableViewCell* cell = (CreditTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[CreditTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  cell.stamp = (Stamp*)[stampsArray_ objectAtIndex:indexPath.row];
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [stampsArray_ objectAtIndex:indexPath.row];
  UIViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - Private methods.

- (void)loadStampsFromNetwork {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreditsPath delegate:self];
  objectLoader.objectMapping = stampMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:screenName_, @"screen_name", nil];
  [objectLoader send];
}


#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	self.stampsArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  [self.tableView reloadData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadStampsFromNetwork];
    return;
  }
}


@end
