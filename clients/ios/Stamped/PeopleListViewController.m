//
//  PeopleListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleListViewController.h"

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "ProfileViewController.h"
#import "STLoadingMoreTableViewCell.h"
#import "Stamp.h"
#import "Util.h"

static NSString* const kFriendIDsPath = @"/friendships/friends.json";
static NSString* const kFollowerIDsPath = @"/friendships/followers.json";
static NSString* const kLikesIDsPath = @"/stamps/likes/show.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";

@interface PeopleListViewController()
- (void)loadUserIDsFromNetwork;
- (void)loadUserDataFromNetwork;

@property (nonatomic, retain) NSMutableArray* userIDsToBeFetched;
@property (nonatomic, retain) NSMutableArray* peopleArray;
@property (nonatomic, assign) BOOL loadingNextChunk;
@end

@implementation PeopleListViewController

@synthesize userIDsToBeFetched = userIDsToBeFetched_;
@synthesize peopleArray = peopleArray_;
@synthesize loadingNextChunk = loadingNextChunk_;
@synthesize user = user_;
@synthesize stamp = stamp_;
@synthesize tableView = tableView_;

- (id)initWithSource:(PeopleListSourceType)sourceType {
  self = [super initWithNibName:@"PeopleListViewController" bundle:nil];
  if (self) {
    sourceType_ = sourceType;
  }
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userIDsToBeFetched = nil;
  self.peopleArray = nil;
  self.user = nil;
  self.stamp = nil;
  self.tableView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  if (sourceType_ == PeopleListSourceTypeCredits) {
    self.userIDsToBeFetched = [NSMutableArray arrayWithArray:[(NSSet*)[stamp_.credits valueForKeyPath:@"userID"] allObjects]];
  } else {
    [self loadUserIDsFromNetwork];
  }

  NSString* title = nil;
  if (sourceType_ == PeopleListSourceTypeFollowers)
    title = @"Followers";
  else if (sourceType_ == PeopleListSourceTypeFriends)
    title = @"Following";
  else if (sourceType_ == PeopleListSourceTypeCredits)
    title = @"Credits";
  else if (sourceType_ == PeopleListSourceTypeLikes)
    title = @"Likes";

  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:title
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
}

- (void)viewDidUnload {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userIDsToBeFetched = nil;
  self.peopleArray = nil;
  self.tableView = nil;
  [super viewDidUnload];
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
  NSInteger count = self.peopleArray.count;
  if (self.userIDsToBeFetched.count > 0)
    ++count;

  return count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == self.peopleArray.count) {
    if (!loadingNextChunk_)
      [self loadUserDataFromNetwork];

    loadingNextChunk_ = YES;
    return [STLoadingMoreTableViewCell cell];
  }
  
  static NSString* CellIdentifier = @"Cell";
  PeopleTableViewCell* cell = (PeopleTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[PeopleTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.user = [self.peopleArray objectAtIndex:indexPath.row];
  
  return cell;
}

#pragma mark - RKRequestDelegate methods.

- (void)request:(RKRequest*)request didLoadResponse:(RKResponse*)response {
  if (!response.isOK)
    return;
  
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser)
    return;

  if ([request.resourcePath rangeOfString:kFriendIDsPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kFollowerIDsPath].location != NSNotFound ||
      [request.resourcePath rangeOfString:kLikesIDsPath].location != NSNotFound) {
    NSError* error = NULL;
    id responseObj = [response parsedBody:&error];
    if (error) {
      NSLog(@"Problem parsing response JSON: %@", error);
    } else {
      self.userIDsToBeFetched = [NSMutableArray arrayWithArray:[responseObj objectForKey:@"user_ids"]];
      if (userIDsToBeFetched_.count > 0) {
        [self loadUserDataFromNetwork];
      } else {
        self.userIDsToBeFetched = nil;
      }
    }
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  User* currentUser = [AccountManager sharedManager].currentUser;
  if (!currentUser || [objectLoader.resourcePath rangeOfString:kUserLookupPath].location == NSNotFound)
    return;

  if (!self.peopleArray)
    self.peopleArray = [NSMutableArray array];
  
  NSArray* sortedArray = [objects sortedArrayUsingComparator:(NSComparator)^(id a, id b) {
    NSNumber* first = [NSNumber numberWithUnsignedInteger:[self.userIDsToBeFetched indexOfObject:[(User*)a userID]]];
    NSNumber* second = [NSNumber numberWithUnsignedInteger:[self.userIDsToBeFetched indexOfObject:[(User*)b userID]]];
    return [first compare:second];
  }];
  [self.peopleArray addObjectsFromArray:sortedArray];
  NSUInteger userIDCount = userIDsToBeFetched_.count;
  NSArray* subArray = [userIDsToBeFetched_ subarrayWithRange:NSMakeRange(0, MIN(100, userIDCount))];
  [self.userIDsToBeFetched removeObjectsInArray:subArray];
  [self.tableView reloadData];
  loadingNextChunk_ = NO;
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadUserIDsFromNetwork];
    return;
  }
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row >= self.peopleArray.count)
    return;

  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = [self.peopleArray objectAtIndex:indexPath.row];
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - People

- (void)loadUserDataFromNetwork {
  if (!userIDsToBeFetched_ || userIDsToBeFetched_.count == 0)
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUserLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSUInteger userIDCount = userIDsToBeFetched_.count;
  NSArray* subArray = [userIDsToBeFetched_ subarrayWithRange:NSMakeRange(0, MIN(100, userIDCount))];
  objectLoader.params = [NSDictionary dictionaryWithObject:[subArray componentsJoinedByString:@","]
                                                    forKey:@"user_ids"];
  objectLoader.method = RKRequestMethodPOST;
  [objectLoader send];
}

- (void)loadUserIDsFromNetwork {
  NSString* path = nil;
  switch (sourceType_) {
    case PeopleListSourceTypeFriends:
      path = kFriendIDsPath;
      break;
    case PeopleListSourceTypeFollowers:
      path = kFollowerIDsPath;
      break;
    case PeopleListSourceTypeLikes:
      path = kLikesIDsPath;
      break;
    default:
      break;
  }
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:path delegate:self];
  if (user_ && (sourceType_ == PeopleListSourceTypeFriends || sourceType_ == PeopleListSourceTypeFollowers))
    request.params = [NSDictionary dictionaryWithObject:user_.userID forKey:@"user_id"];
  else if (stamp_ && sourceType_ == PeopleListSourceTypeLikes)
    request.params = [NSDictionary dictionaryWithObject:stamp_.stampID forKey:@"stamp_id"];
  [request send];
}

@end
