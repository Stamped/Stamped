//
//  STUserListViewController.m
//  Stamped
//
//  Created by Landon Judkins on 6/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserListViewController.h"

@interface STUserListViewController ()

@property (nonatomic, readwrite, assign) BOOL reloading;

@end

@implementation STUserListViewController

@synthesize reloading = _reloading;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view.
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}

/*
#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return 0;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    //id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    //return [[[STActivityCell alloc] initWithActivity:activity andScope:self.scope] autorelease];
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    //id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    //if (activity.action) {
    //    [[STActionManager sharedActionManager] didChooseAction:activity.action withContext:[STActionContext context]];
    //}
}


#pragma mark - DataSource Reloading

- (void)reloadStampedData {
    STGenericSlice* slice = [[[STGenericSlice alloc] init] autorelease];
    slice.limit = [NSNumber numberWithInteger:100];
    if (self.scope == STStampedAPIScopeYou) {
        [[STStampedAPI sharedInstance] activitiesForYouWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
            if (activities) {
                newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
                [self.tableView reloadData];
            }
            [self dataSourceDidFinishLoading];
        }];
    }
    else {
        [[STStampedAPI sharedInstance] activitiesForFriendsWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
            if (activities) {
                newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
                [self.tableView reloadData];
            }
            [self dataSourceDidFinishLoading];
        }];
    }
}


#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return self.reloading;
}

- (void)loadNextPage {
}

- (BOOL)dataSourceHasMoreData {
    return self.reloading;
}

- (void)reloadDataSource {
    self.reloading = YES;
    [self reloadStampedData];
    [super reloadDataSource];
}

- (void)dataSourceDidFinishLoading {
    self.reloading = NO;
    [super dataSourceDidFinishLoading];
}

- (BOOL)dataSourceIsEmpty {
    return self.newsItems.count == 0;
}

- (void)noDataTapped:(id)notImportant {
    [Util warnWithMessage:@"not implemented yet..." andBlock:nil];
}

- (void)setupNoDataView:(NoDataView*)view {
    
    [view setupWithTitle:@"No news" detailTitle:@"No news found."];
    
}
*/

@end
