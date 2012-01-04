//
//  RelationshipsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "RelationshipsViewController.h"

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "ProfileViewController.h"
#import "Util.h"

static NSString* const kFriendIDsPath = @"/friendships/friends.json";
static NSString* const kFollowerIDsPath = @"/friendships/followers.json";
static NSString* const kUserLookupPath = @"/users/lookup.json";

@interface RelationshipsViewController()
- (void)loadRelationshipsFromNetwork;
- (void)loadUserDataFromNetwork;

@property (nonatomic, retain) NSMutableArray* userIDsToBeFetched;
@property (nonatomic, retain) NSMutableArray* peopleArray;
@end

@implementation RelationshipsViewController

@synthesize userIDsToBeFetched = userIDsToBeFetched_;
@synthesize peopleArray = peopleArray_;
@synthesize user = user_;
@synthesize tableView = tableView_;

- (id)initWithRelationship:(RelationshipType)relationshipType {
  self = [super initWithNibName:@"RelationshipsViewController" bundle:nil];
  if (self) {
    relationshipType_ = relationshipType;
  }
  return self;
}

- (void)dealloc {
  self.userIDsToBeFetched = nil;
  self.peopleArray = nil;
  self.user = nil;
  self.tableView = nil;
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadRelationshipsFromNetwork];
  NSString* title = nil;
  if (relationshipType_ == RelationshipTypeFollowers)
    title = @"Followers";
  else if (relationshipType_ == RelationshipTypeFriends)
    title = @"Following";

  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:title
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.userIDsToBeFetched = nil;
  self.peopleArray = nil;
  self.user = nil;
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

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return self.peopleArray.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
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
      [request.resourcePath rangeOfString:kFollowerIDsPath].location != NSNotFound) {
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
  NSLog(@"People array: %@", [self.peopleArray valueForKeyPath:@"userID"]);
  [self.userIDsToBeFetched removeObjectsInArray:[objects valueForKeyPath:@"userID"]];
  NSLog(@"New user IDs count: %d", self.userIDsToBeFetched.count);
  [self.tableView reloadData];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadRelationshipsFromNetwork];
    return;
  }
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
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

- (void)loadRelationshipsFromNetwork {
  NSString* path = relationshipType_ == RelationshipTypeFollowers ? kFollowerIDsPath : kFriendIDsPath;
  RKRequest* request = [[RKClient sharedClient] requestWithResourcePath:path delegate:self];
  request.params = [NSDictionary dictionaryWithObject:user_.userID forKey:@"user_id"];
  [request send];
}

@end
