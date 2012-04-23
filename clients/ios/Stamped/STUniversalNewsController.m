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

@interface STUniversalNewsCell : UITableViewCell

- (id)initWithActivity:(id<STActivity>)activity;

@end

@implementation STUniversalNewsCell

- (id)initWithActivity:(id<STActivity>)activity {
  self = [super initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"test"];
  if (self) {
    self.textLabel.text = activity.header;
    self.detailTextLabel.text = activity.body;
  }
  return self;
}

@end

@interface STUniversalNewsController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) NSMutableArray* newsItems;

@end

@implementation STUniversalNewsController

@synthesize newsItems = newsItems_;

- (id)init {
  self = [super initWithHeaderHeight:0];
  if (self) {
    STGenericSlice* slice = [[[STGenericSlice alloc] init] autorelease];
    slice.limit = [NSNumber numberWithInteger:100];
    [self reloadStampedData];
  }
  return self;
}

- (void)backButtonClicked:(id)button {
  [[STRootMenuView sharedInstance] toggle];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self;
  self.tableView.dataSource = self;
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.newsItems) {
    NSLog(@"heraerae%d",self.newsItems.count);
    return self.newsItems.count;
  }
  NSLog(@"alksfd");
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
  return [[[STUniversalNewsCell alloc] initWithActivity:activity] autorelease];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
  if (activity.action) {
    [[STActionManager sharedActionManager] didChooseAction:activity.action withContext:[STActionContext context]];
  }
}

- (void)reloadStampedData {
  [[STStampedAPI sharedInstance] activitiesForYouWithGenericSlice:nil andCallback:^(NSArray<STActivity> *activities, NSError *error) {
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

@end
