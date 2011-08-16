//
//  InboxViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxViewController.h"

#import <CoreText/CoreText.h>
#import <MapKit/MapKit.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "Stamp.h"
#import "STNavigationBar.h"
#import "InboxTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kFilterRowHeight = 44.0;

typedef enum {
  StampsListFilterTypeBook,
  StampsListFilterTypeFilm,
  StampsListFilterTypeMusic,
  StampsListFilterTypePlace,
  StampsListFilterTypeOther,
  StampsListFilterTypeAll
} StampsListFilterType;

@interface InboxViewController ()
- (void)loadStampsFromDataStore;
- (void)loadStampsFromNetwork;
- (void)stampWasCreated:(NSNotification*)notification;
- (void)mapButtonWasPressed:(NSNotification*)notification;
- (void)listButtonWasPressed:(NSNotification*)notification;

@property (nonatomic, copy) NSArray* filterButtons;
@property (nonatomic, copy) NSArray* entitiesArray;
@property (nonatomic, copy) NSArray* filteredEntitiesArray;
@end

@implementation InboxViewController

@synthesize mapView = mapView_;
@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize filterButtons = filterButtons_;
@synthesize filterView = filterView_;
@synthesize foodFilterButton = foodFilterButton_;
@synthesize booksFilterButton = booksFilterButton_;
@synthesize filmFilterButton = filmFilterButton_;
@synthesize musicFilterButton = musicFilterButton_;
@synthesize otherFilterButton = otherFilterButton_;

- (void)dealloc {
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.filterButtons = nil;
  self.filterView = nil;
  self.foodFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmFilterButton = nil;
  self.musicFilterButton = nil;
  self.otherFilterButton = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  [super dealloc];
}

- (void)mapButtonWasPressed:(NSNotification*)notification {
  [UIView animateWithDuration:0.5 animations:^{ mapView_.alpha = 1.0; }];
}

- (void)listButtonWasPressed:(NSNotification*)notification {
  [UIView animateWithDuration:0.5 animations:^{ mapView_.alpha = 0.0; }];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(stampWasCreated:)
                                               name:kStampWasCreatedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(mapButtonWasPressed:)
                                               name:kMapViewButtonPressedNotification
                                             object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(listButtonWasPressed:)
                                               name:kListViewButtonPressedNotification
                                             object:nil];
  mapView_ = [[MKMapView alloc] initWithFrame:self.view.frame];
  mapView_.alpha = 0.0;
  [self.view addSubview:mapView_];
  [mapView_ release];

  self.filterButtons =
      [NSArray arrayWithObjects:(id)foodFilterButton_,
                                (id)booksFilterButton_,
                                (id)filmFilterButton_,
                                (id)musicFilterButton_,
                                (id)otherFilterButton_, nil];
  
  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  [self loadStampsFromDataStore];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  self.filterView = nil;
  self.filterButtons = nil;
  self.foodFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmFilterButton = nil;
  self.musicFilterButton = nil;
  self.otherFilterButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (!userDidScroll_)
    self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
}

- (void)viewDidAppear:(BOOL)animated {
  if (foodFilterButton_.selected) {
    StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
    STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
    [navBar setButtonFlipped:YES animated:animated];
  }
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  if (foodFilterButton_.selected) {
    StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
    STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
    [navBar setButtonFlipped:NO animated:NO];
  }  
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)loadStampsFromDataStore {
  self.entitiesArray = nil;
	NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
	NSArray* results = [Stamp objectsWithFetchRequest:request];

  results = [results valueForKeyPath:@"@distinctUnionOfObjects.entityObject"];
  descriptor = [NSSortDescriptor sortDescriptorWithKey:@"stamps.@max.created" ascending:NO];
  self.entitiesArray = [results sortedArrayUsingDescriptors:[NSArray arrayWithObject:descriptor]];
  
  [self filterButtonPushed:nil];
}

- (void)loadStampsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  NSString* authToken = [AccountManager sharedManager].authToken.accessToken;
  NSString* resourcePath = [@"/collections/inbox.json" appendQueryParams:[NSDictionary dictionaryWithObject:authToken forKey:@"oauth_token"]];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:stampMapping
                                  delegate:self];
}

- (void)stampWasCreated:(NSNotification*)notification {
  [self loadStampsFromDataStore];
  self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
}

#pragma mark - Filter stuff

- (IBAction)filterButtonPushed:(id)sender {
  filteredEntitiesArray_ = nil;
  // In case the nav bar map button needs to be flipped.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  STNavigationBar* navBar = (STNavigationBar*)delegate.navigationController.navigationBar;
  [navBar setButtonFlipped:NO animated:NO];

  UIButton* selectedButton = (UIButton*)sender;
  for (UIButton* button in self.filterButtons)
    button.selected = (button == selectedButton && !button.selected);

  if (selectedButton && !selectedButton.selected) {
    self.filteredEntitiesArray = entitiesArray_;
    [self.tableView reloadData];
    return;
  } else if (!selectedButton) {
    // Initial load from datastore.
    self.filteredEntitiesArray = entitiesArray_;
    [self.tableView reloadData];
  }

  NSString* filterString = nil;
  if (selectedButton == foodFilterButton_) {
    filterString = @"food";
    [navBar setButtonFlipped:YES animated:YES];
  } else if (selectedButton == booksFilterButton_) {
    filterString = @"books";
  } else if (selectedButton == filmFilterButton_) {
    filterString = @"film";
  } else if (selectedButton == musicFilterButton_) {
    filterString = @"music";
  } else if (selectedButton == otherFilterButton_) {
    filterString = @"other";
  }
  if (filterString) {
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"category == %@", filterString];
    self.filteredEntitiesArray = [entitiesArray_ filteredArrayUsingPredicate:filterPredicate];
    [self.tableView reloadData];
  }
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return [filteredEntitiesArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  cell.entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"InboxLastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
	[self loadStampsFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadStampsFromNetwork];
    return;
  }

  [self setIsLoading:NO];
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor whiteColor];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Entity* entity = [filteredEntitiesArray_ objectAtIndex:indexPath.row];
  Stamp* stamp = nil;
  if (entity.stamps.count > 0) {
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
    NSArray* sortedStamps = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    stamp = [sortedStamps lastObject];
  } else {
    stamp = [entity.stamps anyObject];
  }
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];

  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - STReloadableTableView methods.

- (void)userPulledToReload {
  [super userPulledToReload];
  [self loadStampsFromNetwork];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  userDidScroll_ = YES;
  [[NSNotificationCenter defaultCenter] postNotificationName:kInboxTableDidScrollNotification
                                                      object:scrollView];
  [super scrollViewDidScroll:scrollView];
}

- (void)scrollViewDidEndDragging:(UIScrollView*)scrollView willDecelerate:(BOOL)decelerate {
  [super scrollViewDidEndDragging:scrollView willDecelerate:decelerate];
}

@end
