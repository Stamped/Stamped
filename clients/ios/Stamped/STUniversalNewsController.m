//
//  STUniversalNewsController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUniversalNewsController.h"
#import "STRootMenuView.h"
#import "STStampedAPI.h"
#import "STActivity.h"
#import "STActionManager.h"
#import "ECSlidingViewController.h"
#import "STActivityCell.h"
#import "Util.h"

@interface STUniversalNewsController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) NSMutableArray* newsItems;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;

@end

@implementation STUniversalNewsController

@synthesize newsItems = newsItems_;
@synthesize scope = scope_;

- (void)updateToggleButton {
  NSString* text;
  if (scope_ == STStampedAPIScopeYou) {
    text = @"Friends";
  }
  else {
    text = @"You";
  }
  UIBarButtonItem* rightButton = [[[UIBarButtonItem alloc] initWithTitle:text
                                                                   style:UIBarButtonItemStylePlain
                                                                  target:self
                                                                  action:@selector(toggleButtonClicked:)] autorelease];
  self.navigationItem.rightBarButtonItem = rightButton;
}

- (void)setScope:(STStampedAPIScope)scope {
  scope_ = scope;
  [self updateToggleButton];
  [self reloadStampedData];
}

- (id)init {
  self = [super initWithHeaderHeight:0];
  if (self) {
    scope_ = STStampedAPIScopeYou;
    [self updateToggleButton];
  }
  return self;
}

- (void)backButtonClicked:(id)button {
  [self.slidingViewController anchorTopViewTo:ECRight];
}

- (void)toggleButtonClicked:(id)button {
  if (self.scope == STStampedAPIScopeYou) {
    self.scope = STStampedAPIScopeFriends;
  }
  else {
    self.scope = STStampedAPIScopeYou;
  }
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self;
  self.tableView.dataSource = self;
  [Util addHomeButtonToController:self withBadge:NO];
  [self reloadStampedData];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.newsItems) {
    return self.newsItems.count;
  }
  return 0;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
  return [STActivityCell heightForCellWithActivity:activity andScope:self.scope];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
  return [[[STActivityCell alloc] initWithActivity:activity andScope:self.scope] autorelease];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
  if (activity.action) {
    [[STActionManager sharedActionManager] didChooseAction:activity.action withContext:[STActionContext context]];
  }
}

- (void)reloadStampedData {
  STGenericSlice* slice = [[[STGenericSlice alloc] init] autorelease];
  slice.limit = [NSNumber numberWithInteger:100];
  if (self.scope == STStampedAPIScopeYou) {
    [[STStampedAPI sharedInstance] activitiesForYouWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
      if (activities) {
        NSLog(@"activities:%@",activities);
        newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
        [self.tableView reloadData];
      }
      else {
        NSLog(@"activity error: %@",error);
      }
    }];
  }
  else {
    [[STStampedAPI sharedInstance] activitiesForFriendsWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
      if (activities) {
        NSLog(@"activities:%@",activities);
        newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
        [self.tableView reloadData];
      }
      else {
        NSLog(@"activity error: %@",error);
      }
    }];
  }
}

@end
