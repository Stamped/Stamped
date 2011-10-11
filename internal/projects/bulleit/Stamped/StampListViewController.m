//
//  StampListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "StampListViewController.h"

#import <RestKit/CoreData/CoreData.h>

#import "Entity.h"
#import "Stamp.h"
#import "StampDetailViewController.h"
#import "AccountManager.h"
#import "InboxTableViewCell.h"

static NSString* const kUserStampsPath = @"/collections/user.json";

@interface StampListViewController ()
- (void)loadStampsFromNetwork;
- (void)loadStampsFromDataStore;
- (void)sortStamps;
- (void)filterStamps;

@property (nonatomic, retain) NSDate* oldestInBatch;
@property (nonatomic, copy) NSArray* stampsArray;
@property (nonatomic, copy) NSArray* filteredStampsArray;
@property (nonatomic, assign) StampFilterType selectedFilterType;
@property (nonatomic, assign) StampSortType selectedSortType;
@property (nonatomic, copy) NSString* searchQuery;
@end

@implementation StampListViewController

@synthesize tableView = tableView_;
@synthesize stampsArray = stampsArray_;
@synthesize filteredStampsArray = filteredStampsArray_;
@synthesize stampsAreTemporary = stampsAreTemporary_;
@synthesize user = user_;
@synthesize oldestInBatch = oldestInBatch_;
@synthesize selectedSortType = selectedSortType_;
@synthesize selectedFilterType = selectedFilterType_;
@synthesize searchQuery = searchQuery_;
@synthesize stampFilterBar = stampFilterBar_;

- (id)init {
  self = [self initWithNibName:@"StampListViewController" bundle:nil];
  if (self) {
    stampsAreTemporary_ = YES;
  }
  return self;
}

- (void)dealloc {
  self.user = nil;
  self.stampsArray = nil;
  self.tableView = nil;
  self.oldestInBatch = nil;
  self.searchQuery = nil;
  self.stampFilterBar = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

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
  [stampFilterBar_.locationManager stopUpdatingLocation];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadStampsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.tableView = nil;
  self.stampFilterBar = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)setStampsAreTemporary:(BOOL)stampsAreTemporary {
  stampsAreTemporary_ = stampsAreTemporary;
  
  for (Stamp* stamp in stampsArray_) {
    stamp.temporary = [NSNumber numberWithBool:stampsAreTemporary];
    [stamp.managedObjectContext save:NULL];
  }
}

- (void)filterStamps {
  if (selectedFilterType_ == StampFilterTypeNone) {
    // No need to filter.
    self.filteredStampsArray = [NSArray arrayWithArray:stampsArray_];
    return;
  }
  
  NSString* filterString = nil;
  switch (selectedFilterType_) {
    case StampFilterTypeBook:
      filterString = @"book";
      break;
    case StampFilterTypeFood:
      filterString = @"food";
      break;
    case StampFilterTypeFilm:
      filterString = @"film";
      break;
    case StampFilterTypeMusic:
      filterString = @"music";
      break;
    case StampFilterTypeOther:
      filterString = @"other";
      break;
    default:
      NSLog(@"Invalid filter string...");
      break;
  }
  if (filterString) {
    NSPredicate* filterPredicate = [NSPredicate predicateWithFormat:@"entityObject.category == %@", filterString];
    self.filteredStampsArray = [stampsArray_ filteredArrayUsingPredicate:filterPredicate];
  }
}

- (void)sortStamps {
  NSSortDescriptor* desc = nil;
  switch (selectedSortType_) {
    case StampSortTypeTime:
      desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
      break;
    case StampSortTypePopularity:
      desc = [NSSortDescriptor sortDescriptorWithKey:@"entityObject.stamps.@count" ascending:NO];
      break;
    case StampSortTypeDistance: {
      CLLocation* currentLocation = stampFilterBar_.currentLocation;
      if (!currentLocation)
        break;
      
      self.filteredStampsArray = [filteredStampsArray_ sortedArrayUsingComparator:^NSComparisonResult(id obj1, id obj2) {
        Stamp* firstStamp = (Stamp*)obj1;
        Stamp* secondStamp = (Stamp*)obj2;
        
        NSNumber* firstDistance = nil;
        NSNumber* secondDistance = nil;
        
        if (!firstStamp.entityObject.location && !secondStamp.entityObject.location)
          return NSOrderedSame;
        else if (!firstStamp.entityObject.location && secondStamp.entityObject.location)
          return NSOrderedDescending;
        else if (firstStamp.entityObject.location && !secondStamp.entityObject.location)
          return NSOrderedAscending;
        
        firstDistance = [NSNumber numberWithDouble:[firstStamp.entityObject.location distanceFromLocation:currentLocation]];
        firstStamp.entityObject.cachedDistance = firstDistance;
        secondDistance = [NSNumber numberWithDouble:[secondStamp.entityObject.location distanceFromLocation:currentLocation]];
        secondStamp.entityObject.cachedDistance = secondDistance;
        return [firstDistance compare:secondDistance];
      }];
      break;
    }
    default:
      break;
  }
  if (!desc)
    return;
  
  self.filteredStampsArray = [filteredStampsArray_ sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
}

#pragma mark - STStampFilterBarDelegate methods.

- (void)stampFilterBar:(STStampFilterBar*)bar
       didSelectFilter:(StampFilterType)filterType
          withSortType:(StampSortType)sortType
              andQuery:(NSString*)query {
  if (![query isEqualToString:searchQuery_]) {
    self.searchQuery = query;
    [self loadStampsFromDataStore];
  }

  selectedFilterType_ = filterType;
  [self filterStamps];
  
  selectedSortType_ = sortType;
  [self sortStamps];
  
  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return self.filteredStampsArray.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"StampCell";
  InboxTableViewCell* cell = (InboxTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (!cell)
    cell = [[[InboxTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  
  cell.sortType = selectedSortType_;
  cell.stamp = (Stamp*)[filteredStampsArray_ objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  Stamp* stamp = [filteredStampsArray_ objectAtIndex:indexPath.row];
  StampDetailViewController* detailViewController = [[StampDetailViewController alloc] initWithStamp:stamp];
  
  [self.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath rangeOfString:kUserStampsPath].location != NSNotFound) {
    self.oldestInBatch = [objects.lastObject modified];

    [self loadStampsFromDataStore];
    self.stampsAreTemporary = stampsAreTemporary_;  // Just fire off the setters logic.
    if (objects.count < 10) {
      self.oldestInBatch = nil;
    } else {
      [self loadStampsFromNetwork];
    }
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [objectLoader send];
    return;
  }
}

- (void)loadStampsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserStampsPath
                                                                    delegate:self];
  objectLoader.objectMapping = stampMapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:user_.userID, @"user_id",
      @"1", @"quality", @"0", @"since", nil];
  if (oldestInBatch_)
    [params setObject:[NSString stringWithFormat:@"%.0f", oldestInBatch_.timeIntervalSince1970] forKey:@"before"];

  objectLoader.params = params;
  [objectLoader send];
}

- (void)loadStampsFromDataStore {
  self.stampsArray = nil;
  NSArray* searchTerms = [searchQuery_ componentsSeparatedByString:@" "];

  NSPredicate* p = [NSPredicate predicateWithFormat:@"user.screenName == %@", user_.screenName];
  if (searchTerms.count == 1 && searchQuery_.length) {
    p = [NSPredicate predicateWithFormat:
         @"(user.screenName == %@) AND ((blurb contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
         user_.screenName, searchQuery_, searchQuery_, searchQuery_, searchQuery_];
  } else if (searchTerms.count > 1) {
    NSMutableArray* subPredicates = [NSMutableArray array];
    for (NSString* term in searchTerms) {
      if (!term.length)
        continue;
      
      NSPredicate* p = [NSPredicate predicateWithFormat:
                        @"(user.screenName == %@) AND ((blurb contains[cd] %@) OR (entityObject.title contains[cd] %@) OR (entityObject.subtitle contains[cd] %@))",
                        user_.screenName, term, term, term, term];
      [subPredicates addObject:p];
    }
    p = [NSCompoundPredicate andPredicateWithSubpredicates:subPredicates];
  }
  NSFetchRequest* request = [Stamp fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
  [request setPredicate:p];
	self.stampsArray = [Stamp objectsWithFetchRequest:request];
  
  [self filterStamps];
  [self sortStamps];
  [self.tableView reloadData];
}


@end
