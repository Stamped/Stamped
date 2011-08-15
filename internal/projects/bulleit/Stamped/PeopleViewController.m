//
//  PeopleViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleViewController.h"

#import "AccountManager.h"
#import "UserImageView.h"
#import "UIColor+Stamped.h"

@implementation PeopleViewController

@synthesize currentUserView = currentUserView_;
@synthesize userStampImageView = userStampImageView_;
@synthesize userFullNameLabel = userFullNameLabel_;
@synthesize userScreenNameLabel = userScreenNameLabel_;
@synthesize addFriendsButton = addFriendsButton_;

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  User* currentUser = [AccountManager sharedManager].currentUser;
  currentUserView_.imageURL = currentUser.profileImageURL;
  userStampImageView_.image = currentUser.stampImage;
  userScreenNameLabel_.text = currentUser.screenName;
  userScreenNameLabel_.textColor = [UIColor lightGrayColor];
  userFullNameLabel_.text =  [[NSArray arrayWithObjects:currentUser.firstName, currentUser.lastName, nil] componentsJoinedByString:@" "];
  userFullNameLabel_.textColor = [UIColor stampedBlackColor];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.currentUserView = nil;
  self.userStampImageView = nil;
  self.userFullNameLabel = nil;
  self.userScreenNameLabel = nil;
  self.addFriendsButton = nil;
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

- (void)userPulledToReload {
  [self setIsLoading:NO];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  // Return the number of sections.
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString *CellIdentifier = @"Cell";
  
  UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
      cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
  }
  
  // Configure the cell...
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  // Navigation logic may go here. Create and push another view controller.
  /*
   <#DetailViewController#> *detailViewController = [[<#DetailViewController#> alloc] initWithNibName:@"<#Nib name#>" bundle:nil];
   // ...
   // Pass the selected object to the new view controller.
   [self.navigationController pushViewController:detailViewController animated:YES];
   [detailViewController release];
   */
}

@end
