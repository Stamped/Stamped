//
//  CreditsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreditsViewController.h"

#import "AccountManager.h"
#import "CreditTableViewCell.h"
#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "StampDetailViewController.h"
#import "STLoadingMoreTableViewCell.h"

static NSString* const kCreditsPath = @"/collections/credit.json";

@interface CreditsViewController ()
- (void)loadStampsFromNetwork;
- (void)reloadTableData;

@property (nonatomic, retain) NSMutableArray* stampsArray;
@property (nonatomic, assign) BOOL loadingNextChunk;
@property (nonatomic, assign) BOOL loadedAllCredits;
@end

@implementation CreditsViewController

@synthesize tableView = tableView_;
@synthesize stampsArray = stampsArray_;
@synthesize loadingNextChunk = loadingNextChunk_;
@synthesize loadedAllCredits = loadedAllCredits_;
@synthesize screenName = screenName_;
@synthesize user = user_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.tableView = nil;
  self.stampsArray = nil;
  self.screenName = nil;
  self.user = nil;
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [super dealloc];
}

#pragma mark - View lifecycle

- (id)initWithUser:(User*)user {
  self.user = user;
  self.screenName = user.screenName;
  self.stampsArray = [NSMutableArray array];

  return [self initWithNibName:@"CreditsViewController" bundle:nil];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Credits"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
  
  User* currentUser = [AccountManager sharedManager].currentUser;
  if ([currentUser.userID isEqualToString:user_.userID] && currentUser.numCredits.integerValue == 0) {
    UIImageView* emptyView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"empty_credits"]];
    [self.view insertSubview:emptyView atIndex:0];
    [emptyView release];
  }
  if (stampsArray_.count == 0) {
    self.tableView.hidden = YES;
    [self loadStampsFromNetwork];
  }
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.tableView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [tableView_ deselectRowAtIndexPath:tableView_.indexPathForSelectedRow
                            animated:animated];
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

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  NSInteger count = stampsArray_.count;
  if (!loadedAllCredits_)
    ++count;

  return count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == self.stampsArray.count) {
    if (!loadingNextChunk_)
      [self loadStampsFromNetwork];
    
    loadingNextChunk_ = YES;
    return [STLoadingMoreTableViewCell cell];
  }
  
  static NSString* CellIdentifier = @"Cell";
  CreditTableViewCell* cell = (CreditTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[CreditTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.stamp = (Stamp*)[stampsArray_ objectAtIndex:indexPath.row];
  cell.creditedUser = self.user;
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
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObjectsAndKeys:screenName_, @"screen_name", @"0", @"since", nil];
  if (stampsArray_.count > 0) {
    Stamp* oldestStamp = stampsArray_.lastObject;
    NSString* dateString = [NSString stringWithFormat:@"%.0f", oldestStamp.created.timeIntervalSince1970];
    [params setObject:dateString forKey:@"before"];
  }
  objectLoader.params = params;
  [objectLoader send];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if (objects.count < 20)
    loadedAllCredits_ = YES;

  loadingNextChunk_ = NO;

  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:NO];
  NSArray* sortedStamps = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  for (Stamp* s in sortedStamps) {
    if (![stampsArray_ containsObject:s])
      [stampsArray_ addObject:s];
  }
  [self reloadTableData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadStampsFromNetwork];
    return;
  }
}

- (void)reloadTableData {
  [self.tableView reloadData];
  self.tableView.hidden = [self.tableView numberOfRowsInSection:0] == 0;
}

@end
