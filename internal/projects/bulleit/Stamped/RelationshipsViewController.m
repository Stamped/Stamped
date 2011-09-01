//
//  RelationshipsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "RelationshipsViewController.h"

#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "PeopleTableViewCell.h"
#import "ProfileViewController.h"


static NSString* const kFriendsPath = @"/temp/friends.json";
static NSString* const kFollowersPath = @"/temp/followers.json";

@interface RelationshipsViewController()
- (void)loadRelationshipsFromNetwork;
@property (nonatomic, copy) NSArray* peopleArray;
@end

@implementation RelationshipsViewController

@synthesize peopleArray = peopleArray_;
@synthesize user = user_;

- (id)initWithRelationship:(RelationshipType)relationshipType {
  self = [super initWithNibName:@"RelationshipsViewController" bundle:nil];
  if (self) {
    relationshipType_ = relationshipType;
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)userPulledToReload {
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    [self setIsLoading:NO];
    return;
  }
  [self loadRelationshipsFromNetwork];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  [self loadRelationshipsFromNetwork];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.peopleArray = nil;
  self.user = nil;
}

- (void)viewWillAppear:(BOOL)animated {
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

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  self.peopleArray = nil;
  self.peopleArray = [objects sortedArrayUsingDescriptors:[NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"firstName" ascending:YES]]];
  [self.tableView reloadData];
  [self setIsLoading:NO];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadRelationshipsFromNetwork];
    return;
  }
  
  [self setIsLoading:NO];
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = [self.peopleArray objectAtIndex:indexPath.row];
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

#pragma mark - People

- (void)loadRelationshipsFromNetwork {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;
  
  NSString* path = relationshipType_ == RelationshipTypeFollowers ? kFollowersPath : kFriendsPath;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* userMapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  NSString* userID = user_.userID;
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.objectMapping = userMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:userID, @"user_id", nil];
  [objectLoader send];
}

@end
