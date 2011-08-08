//
//  InboxViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "Stamp.h"
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

@property (nonatomic, copy) NSArray* filterButtons;
@property (nonatomic, copy) NSArray* entitiesArray;
@property (nonatomic, copy) NSArray* filteredEntitiesArray;
@property (nonatomic, assign) UIView* filterView;
@property (nonatomic, retain) UIButton* placesFilterButton;
@property (nonatomic, retain) UIButton* booksFilterButton;
@property (nonatomic, retain) UIButton* filmsFilterButton;
@property (nonatomic, retain) UIButton* musicFilterButton;
@end

@implementation InboxViewController

@synthesize entitiesArray = entitiesArray_;
@synthesize filteredEntitiesArray = filteredEntitiesArray_;
@synthesize filterButtons = filterButtons_;
@synthesize filterView = filterView_;
@synthesize placesFilterButton = placesFilterButton_;
@synthesize booksFilterButton = booksFilterButton_;
@synthesize filmsFilterButton = filmsFilterButton_;
@synthesize musicFilterButton = musicFilterButton_;

- (void)dealloc {
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.filterButtons = nil;
  self.filterView = nil;
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
  self.entitiesArray = nil;
  self.filteredEntitiesArray = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(stampWasCreated:)
                                               name:kStampWasCreatedNotification
                                             object:nil];
  self.filterButtons =
      [NSArray arrayWithObjects:(id)placesFilterButton_,
                                (id)booksFilterButton_,
                                (id)filmsFilterButton_,
                                (id)musicFilterButton_, nil];
  
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
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (!userDidScroll_)
    self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
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
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  NSString* userID = [AccountManager sharedManager].currentUser.userID;
  NSString* resourcePath = [NSString stringWithFormat:@"/collections/inbox.json?authenticated_user_id=%@", userID];
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
  if (selectedButton == placesFilterButton_) {
    filterString = @"Place";
  } else if (selectedButton == booksFilterButton_) {
    filterString = @"Book";
  } else if (selectedButton == filmsFilterButton_) {
    filterString = @"Film";
  } else if (selectedButton == musicFilterButton_) {
    filterString = @"Music";
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
  InboxTableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  cell.entityObject = (Entity*)[filteredEntitiesArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	[[NSUserDefaults standardUserDefaults] setObject:[NSDate date] forKey:@"LastUpdatedAt"];
	[[NSUserDefaults standardUserDefaults] synchronize];
	[self loadStampsFromDataStore];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Error"
                                                   message:[error localizedDescription]
                                                  delegate:nil
                                         cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease];
	[alert show];
	NSLog(@"Hit error: %@", error);
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
