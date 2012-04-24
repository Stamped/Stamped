//
//  STUsersViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUsersViewController.h"
#import "STUserCell.h"
#import "STStampedAPI.h"
#import "STStampedActions.h"
#import "Util.h"

@interface STUsersViewController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, copy) NSArray* userIDs;
@property (nonatomic, readonly, retain) NSMutableArray* userDetails;
@property (nonatomic, readwrite, assign) BOOL failed;

@end

@implementation STUsersViewController

@synthesize userIDs = userIDs_;
@synthesize userDetails = userDetails_;
@synthesize failed = failed_;

- (id)initWithUserIDs:(NSArray*)userIDs
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    userIDs_ = [userIDs retain];
    userDetails_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc
{
  [userIDs_ release];
  [userDetails_ release];
  [super dealloc];
}

- (void)populateUsers {
  NSInteger remaining = self.userIDs.count - self.userDetails.count;
  if (remaining > 0 && !self.failed) {
    NSRange range = NSMakeRange(self.userDetails.count, MIN(20,remaining));
    NSArray* batch = [self.userIDs subarrayWithRange:range];
    [[STStampedAPI sharedInstance] userDetailsForUserIDs:batch andCallback:^(NSArray<STUserDetail> *userDetails, NSError *error) {
      if (userDetails) {
        [self.userDetails addObjectsFromArray:userDetails];
        [self.tableView reloadData];
        [self populateUsers];
      }
      else {
        self.failed = YES;
        [Util warnWithMessage:@"user lookup failed!" andBlock:nil];
      }
    }];
  }
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.rowHeight = 52;
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
  id<STUserDetail> userDetail = [self.userDetails objectAtIndex:indexPath.row];
  STUserCell* cell = [[[STUserCell alloc] initWithReuseIdentifier:@"Todo"] autorelease];
  cell.user = userDetail;
  return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STUserDetail> userDetail = [self.userDetails objectAtIndex:indexPath.row];
  [[STStampedActions sharedInstance] viewUserWithUserID:userDetail.userID];
}


@end
