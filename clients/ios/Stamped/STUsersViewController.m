//
//  STUsersViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUsersViewController.h"

@interface STUsersViewController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, copy) NSArray* userIDs;
@property (nonatomic, readonly, retain) NSMutableArray* userDetails;

@end

@implementation STUsersViewController

@synthesize userIDs = userIDs_;
@synthesize userDetails = userDetails_;

- (id)initWithUserIDs:(NSArray*)userIDs
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    userIDs_ = [userIDs retain];
    userDetails_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)populateUsers {
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self;
  self.tableView.dataSource = self;
  [self populateUsers];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  // Release any retained subviews of the main view.
}


- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.userDetails) {
    return self.userDetails.count;
  }
  return 0;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {

  return [[[STTodoCell alloc] initWithTodo:todo] autorelease];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
}


@end
