//
//  SearchEntitiesViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesViewController.h"

#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "SearchEntitiesTableViewCell.h"
#import "STSearchField.h"
#import "Entity.h"

static NSString* const kSearchPath = @"/entities/search.json";

@interface SearchEntitiesViewController ()
- (void)loadEntitiesFromDataStore;
- (void)searchDataStoreFor:(NSString*)searchText;
- (void)textFieldDidChange:(id)sender;

@property (nonatomic, copy) NSArray* entitiesArray;
@property (nonatomic, copy) NSArray* filteredEntitiesArray;
@property (nonatomic, retain) CLLocationManager* locationManager;
@end

@implementation SearchEntitiesViewController

@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize searchField = searchField_;
@synthesize cancelButton = cancelButton_;
@synthesize locationManager = locationManager_;
@synthesize addStampCell = addStampCell_;
@synthesize addStampLabel = addStampLabel_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

- (void)dealloc {
  self.searchField = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.entitiesArray = nil;
  self.locationManager.delegate = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.view.backgroundColor = [UIColor colorWithWhite:0.972 alpha:1.0];
  self.cancelButton.layer.masksToBounds = YES;
  self.cancelButton.layer.borderColor = [UIColor colorWithWhite:0.6 alpha:0.8].CGColor;
  self.cancelButton.layer.borderWidth = 1.0;
  self.cancelButton.layer.cornerRadius = 5.0;
  self.cancelButton.layer.shadowOpacity = 1.0;

  [self loadEntitiesFromDataStore];
  [self.searchField addTarget:self
                       action:@selector(textFieldDidChange:)
             forControlEvents:UIControlEventEditingChanged];

  self.locationManager = [[[CLLocationManager alloc] init] autorelease];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.searchField = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.entitiesArray = nil;
  self.locationManager = nil;
  self.addStampCell = nil;
  self.addStampLabel = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:YES animated:animated];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self.locationManager startUpdatingLocation];
  [self.searchField becomeFirstResponder];
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [self.navigationController setNavigationBarHidden:NO animated:animated];
  [self.locationManager stopUpdatingLocation];
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)cancelButtonTapped:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

#pragma mark - Core Data Shiz.

- (void)loadEntitiesFromDataStore {
  self.entitiesArray = nil;
  self.entitiesArray = [Entity objectsWithFetchRequest:[Entity fetchRequest]];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  NSInteger numRows = [filteredEntitiesArray_ count];
  if (self.searchField.text.length > 0)
    ++numRows;  // One more for the 'Add new entity' cell.

  return numRows;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == [filteredEntitiesArray_ count])
    return self.addStampCell;
  
  static NSString* CellIdentifier = @"EntityCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[SearchEntitiesTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  
  [(SearchEntitiesTableViewCell*)cell setEntityObject:((Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row])];
  
  return cell;
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != searchField_)
    return YES;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* entityMapping = [objectManager.mappingProvider mappingForKeyPath:@"Entity"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kSearchPath delegate:self];
  objectLoader.objectMapping = entityMapping;
  NSMutableDictionary* params =
      [NSMutableDictionary dictionaryWithKeysAndObjects:@"q", searchField_.text, nil];
  if (self.locationManager.location) {
    CLLocationCoordinate2D coordinate = self.locationManager.location.coordinate;
    NSString* coordString = [NSString stringWithFormat:@"%f,%f", coordinate.latitude, coordinate.longitude];
    [params setObject:coordString forKey:@"coordinates"];
  }  
  objectLoader.params = params;
  [objectLoader send];

  [searchField_ resignFirstResponder];
  return NO;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	self.entitiesArray = nil;
  self.entitiesArray = objects;
  self.filteredEntitiesArray = nil;
  self.filteredEntitiesArray = objects;
  [self.tableView reloadData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];

  [searchField_ becomeFirstResponder];
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Entity* entityObject = nil;
  if (indexPath.row == [filteredEntitiesArray_ count]) {
    entityObject = [Entity object];
    entityObject.title = self.searchField.text;
  } else {
    entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];
  }
  CreateStampViewController* detailViewController =
      [[CreateStampViewController alloc] initWithEntityObject:entityObject];
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (void)searchDataStoreFor:(NSString*)searchText {
  NSPredicate* searchPredicate = [NSPredicate predicateWithFormat:@"title contains[cd] %@", searchText];
  self.filteredEntitiesArray = nil;
  self.filteredEntitiesArray = [self.entitiesArray filteredArrayUsingPredicate:searchPredicate];
  [self.tableView reloadData];
}

- (void)textFieldDidChange:(id)sender {
  if (sender != self.searchField)
    return;

  [self searchDataStoreFor:self.searchField.text];
  self.addStampLabel.text = [NSString stringWithFormat:@"Can\u2019t find \u201c%@\u201d?", self.searchField.text];
}

@end
