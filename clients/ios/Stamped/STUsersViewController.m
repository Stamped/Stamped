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
#import "STGenericTableDelegate.h"
#import "STUserDetailLazyList.h"
#import "STUserCellFactory.h"
#import "STStampedActions.h"
#import "STActionManager.h"

@interface STUsersViewController ()

@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;

@end

@implementation STUsersViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize userIDToStampID = _userIDToStampID;

- (id)initWithUserIDs:(NSArray*)userIDs
{
    self = [super initWithHeaderHeight:0];
    if (self) {
        tableDelegate_ = [[STGenericTableDelegate alloc] init];
        tableDelegate_.pageSize = 32;
        tableDelegate_.preloadBufferSize = 64;
        tableDelegate_.lazyList = [[[STUserDetailLazyList alloc] initWithUserIDs:userIDs] autorelease];
        tableDelegate_.tableViewCellFactory = [STUserCellFactory sharedInstance];
        __block STUsersViewController* weak = self;
        tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
            [weak.tableView reloadData];
        };
        self.tableView.rowHeight = [[STUserCellFactory sharedInstance] loadingCellHeightForTableView:self.tableView andStyle:nil];
        tableDelegate_.selectedCallback = ^(STGenericTableDelegate* tableDelegate, UITableView* tableView, NSIndexPath* path) {
            id<STUserDetail> userDetail = [tableDelegate_.lazyList objectAtIndex:path.row];
            if (userDetail) {
                [self handleSelected:userDetail];
            }
        };
    }
    return self;
}

- (void)dealloc
{
    [tableDelegate_ release];
    [_userIDToStampID release];
    [super dealloc];
}

- (void)handleSelected:(id<STUserDetail>)userDetail {
    NSString* stampID = [self.userIDToStampID objectForKey:userDetail.userID];
    if (stampID) {
        [[STStampedActions sharedInstance] viewStampWithStampID:stampID];
    }
    else {
        STActionContext* context = [STActionContext context];
        context.user = userDetail;
        id<STAction> action = [STStampedActions actionViewUser:userDetail.userID withOutputContext:context];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.tableView.delegate = self.tableDelegate;
    self.tableView.dataSource = self.tableDelegate;
}

- (void)reloadStampedData {
    [self.tableDelegate reloadStampedData];
}

- (void)cancelPendingRequests {
    [super cancelPendingRequests];
    [self.tableDelegate cancelPendingRequests];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}

@end
