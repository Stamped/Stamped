//
//  STUserViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserViewController.h"
#import "STPhotoViewController.h"
#import "STUsersViewController.h"
#import "STUserHeaderView.h"
#import "STSimpleUserDetail.h"
#import "STUserGraphView.h"
#import "STStampCell.h"
#import "STUserStamps.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "FriendStatusButton.h"

#import "STUserCollectionSlice.h"
#import "STUserSource.h"
#import "STNavigationBar.h"
#import "STSimpleSource.h"

@interface STUserViewController ()
@property(nonatomic,readonly) BOOL loadingUser;
@property(nonatomic,retain,readonly) STUserStamps *stamps;
@property(nonatomic,retain) id<STUser> user;
@property(nonatomic,copy) NSString *userIdentifier;
@property(nonatomic,retain,readonly) STUserGraphView *graphView;
@end

@implementation STUserViewController
@synthesize userIdentifier;
@synthesize user=_user;
@synthesize graphView=_graphView;
@synthesize stamps=_stamps;
@synthesize loadingUser=_loadingUser;

- (id)init {
    
    if ((self = [super init])) {
        
        
        
    }
    return self;
    
}

- (id)initWithUserIdentifier:(NSString*)identifier {
    
    if ((self = [super init])) {
        self.userIdentifier = identifier;
        _stamps = [[STUserStamps alloc] init];
        _stamps.userIdentifier = self.userIdentifier;
        [STEvents addObserver:self selector:@selector(stampsFinished:) event:EventTypeUserStampsFinished identifier:self.userIdentifier];
    }
    return self;
    
}

- (id)initWithUser:(id<STUser>)user {
    
    if (self = [super init]) {
        _user = [user retain];
        
        if ([user isKindOfClass:NSClassFromString(@"STSimpleSource")]) {
            
            STSimpleSource *source = (STSimpleSource*)_user;
            self.userIdentifier = source.sourceID;
            self.title = source.name;
            
        } else {
            
            self.userIdentifier = user.userID;
            self.title = user.screenName;
       
        }
        _stamps = [[STUserStamps alloc] init];
        _stamps.userIdentifier = self.userIdentifier;
        [STEvents addObserver:self selector:@selector(stampsFinished:) event:EventTypeUserStampsFinished identifier:self.userIdentifier];

    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];

    if (!self.tableView.tableHeaderView) {
        STUserHeaderView *view = [[STUserHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 155.0f)];
        view.delegate = (id<STUserHeaderViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        view.selectedTab = STUserHeaderTabStamps;
        self.tableView.tableHeaderView = view;
        [view release];
        if (self.user) {
            [view setupWithUser:self.user];
        }
    }
    
    if (LOGGED_IN && IS_CURRENT_USER(self.userIdentifier)) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Edit" style:UIBarButtonItemStyleBordered target:self action:@selector(editProfile:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
    }
    
    [self reloadDataSource];
    
    if (_user && [self.navigationController.navigationBar isKindOfClass:[STNavigationBar class]] && [_user respondsToSelector:@selector(primaryColor)]) {
        [(STNavigationBar*)self.navigationController.navigationBar showUserStrip:YES forUser:_user];
    }
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    
    if ([self.navigationController.navigationBar isKindOfClass:[STNavigationBar class]]) {
        [(STNavigationBar*)self.navigationController.navigationBar showUserStrip:NO forUser:nil];
    }
    
}

- (void)dealloc {
    [STEvents removeObserver:self];
    if (_graphView) {
        [_graphView release], _graphView=nil;
    }
    self.userIdentifier = nil;
    [_user release], _user = nil;    
    [_stamps release], _stamps=nil;
    [super dealloc];
}


#pragma mark - Stamp Notifications

- (void)stampsFinished:(NSNotification*)notification {
    
    NSInteger sections = [self.tableView numberOfSections];
    [self.tableView reloadData];
    [self dataSourceDidFinishLoading];
    
    if (sections == 0 && [self selectedTab] == STUserHeaderTabStamps) {
        [self animateIn];
    }
    
    
}


#pragma mark - Actions

- (void)editProfile:(id)sender {
    
    
}

- (void)toggleFollowing:(FriendStatusButton*)sender {
    
    sender.loading = YES;
    if (sender.status == FriendStatusFollowing) {
        
        [[STStampedAPI sharedInstance] removeFriendForUserID:self.userIdentifier andCallback:^(id<STUserDetail> userDetail, NSError *error) {
            sender.status = FriendStatusNotFollowing;
            sender.loading = NO;
        }];
        
    } else {
        
        [[STStampedAPI sharedInstance] addFriendForUserID:self.userIdentifier andCallback:^(id<STUserDetail> userDetail, NSError *error) {
            sender.status = FriendStatusFollowing;
            sender.loading = NO;
        }];
        
    }
    
}


#pragma mark - Getters

- (STUserHeaderTab)selectedTab {
    
    STUserHeaderView *view = (STUserHeaderView*)self.tableView.tableHeaderView;
    return view.selectedTab;
    
}


#pragma mark - Setters

- (void)setUser:(id<STUser>)user {
    [_user release], _user = nil;    
    _user = [user retain];

    if (self.tableView.tableHeaderView) {
        STUserHeaderView *view = (STUserHeaderView*)self.tableView.tableHeaderView;
        [view setupWithUser:_user];
    }
    
    if (self.graphView) {
        [self.graphView setupWithUser:_user];
    }
    
}


#pragma mark - STUserHeaderViewDelegate

- (void)stUserHeaderViewAvatarTapped:(STUserHeaderView*)view {
    
    STPhotoViewController *controller = [[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:[Util largeProfileImageURLWithUser:self.user]]];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    [controller release];
    
}

- (void)stUserHeaderView:(STUserHeaderView*)view selectedTab:(STUserHeaderTab)tab {
        
    [self.tableView reloadData];
    
    if (tab == STUserHeaderTabGraph) {
        
        if (!_graphView) {
            STUserGraphView *view = [[STUserGraphView alloc] initWithFrame:CGRectMake(0.0f, self.tableView.tableHeaderView.bounds.size.height, self.view.bounds.size.width, 260.0f)];
            view.delegate = (id<STUserGraphViewDelegate>)self;
            [self.tableView addSubview:view];
            _graphView = [view retain];
            [_graphView setupWithUser:self.user];
            [view release];
        }
        
    } else if (tab == STUserHeaderTabInfo) {
        
        
    }
 
    
    if (self.graphView) {
        self.graphView.hidden = (tab != STUserHeaderTabGraph);
    }
    
    [self dataSourceDidFinishLoading];

}

- (void)stUserHeaderView:(STUserHeaderView*)view selectedStat:(STUserHeaderStat)stat {
    
    switch (stat) {
        case STUserHeaderStatCredit:

            [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];

            break;
        case STUserHeaderStatFollowers:
            
            [Util globalLoadingLock];
            [[STStampedAPI sharedInstance] followerIDsForUserID:self.user.userID andCallback:^(NSArray *followerIDs, NSError *error) {
                [Util globalLoadingUnlock];
                if (followerIDs) {
                    STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:followerIDs] autorelease];
                    controller.title = @"Followers";
                    [[Util sharedNavigationController] pushViewController:controller animated:YES];
                }
            }];
            
            break;
        case STUserHeaderStatFollowing:
            
            [Util globalLoadingLock];
            [[STStampedAPI sharedInstance] friendIDsForUserID:self.user.userID andCallback:^(NSArray *friendIDs, NSError *error) {
                [Util globalLoadingUnlock];
                if (friendIDs) {
                    STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:friendIDs] autorelease];
                    controller.title = @"Following";
                    [[Util sharedNavigationController] pushViewController:controller animated:YES];
                }
            }];
            
            break;
        default:
            break;
    }
    
}

- (void)stUserHeaderViewHeightChanged:(STUserHeaderView *)view {
 
    [self.tableView reloadData];
    
}


#pragma mark - STUserGraphViewDelegate

- (void)stUserGraphView:(STUserGraphView*)view selectedCategory:(NSString*)category {
    
    STUserCollectionSlice* slice = [[[STUserCollectionSlice alloc] init] autorelease];
    slice.category = category;
    slice.userID = self.userIdentifier;
    slice.offset = [NSNumber numberWithInteger:0];
    slice.limit = [NSNumber numberWithInteger:1000];
    
    STTableViewController *controller = [[[STTableViewController alloc] initWithHeaderHeight:0] autorelease];
    [controller view];
    STUserSource *source = [[[STUserSource alloc] init] autorelease];
    source.userID = slice.userID;
    source.slice = slice;
    source.table = controller.tableView;
    [controller retainObject:source];
    [self.navigationController pushViewController:controller animated:YES];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {

    id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
    return [STStampCell heightForStamp:stamp];

}

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
    
    if ([self selectedTab] != STUserHeaderTabStamps) return 0;
    return [_stamps isEmpty] ? 0 : 1;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [self.stamps numberOfObject];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.delegate = (id<STStampCellDelegate>)self;
    }
    
    id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
    [cell setupWithStamp:stamp];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
    STActionContext *context = [STActionContext context];
    context.stamp = stamp;
    id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    
}


#pragma mark - STStampCellDelegate

- (void)stStampCellAvatarTapped:(STStampCell*)cell {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
    STUserViewController *controller = [[STUserViewController alloc] initWithUser:stamp.user];
    [self.navigationController pushViewController:controller animated:YES];
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return [self.stamps isReloading] || _loadingUser;
}

- (void)loadNextPage {
    [self.stamps loadNextPage];
}

- (BOOL)dataSourceHasMoreData {
    return [self.stamps hasMore] && [self selectedTab] == STUserHeaderTabStamps;
}

- (void)reloadDataSource {
    if (!self.userIdentifier || _loadingUser) return; // show failed..
    
    _loadingUser = YES;
    [[STStampedAPI sharedInstance] userDetailForUserID:self.userIdentifier andCallback:^(id<STUserDetail> aUser, NSError *error) {
      
        if (aUser) {
            self.user = aUser;
        }
        
        _loadingUser = NO;
        [self dataSourceDidFinishLoading];
        
        if (LOGGED_IN && !IS_CURRENT_USER(self.userIdentifier)) {
            [[STStampedAPI sharedInstance] isFriendForUserID:self.userIdentifier andCallback:^(BOOL isFriend, NSError *error) {
                
                FriendStatusButton *button = [[FriendStatusButton alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 64.0f, 30.0f)];
                [button addTarget:self action:@selector(toggleFollowing:) forControlEvents:UIControlEventTouchUpInside];
                button.status = isFriend ? FriendStatusFollowing : FriendStatusNotFollowing;
                UIBarButtonItem *barButton = [[UIBarButtonItem alloc] initWithCustomView:button];
                self.navigationItem.rightBarButtonItem = barButton;
                [button release];
                [barButton release];
                
                CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"opacity"];
                animation.fromValue = [NSNumber numberWithFloat:0.0f];
                animation.duration = 0.3f;
                [button.layer addAnimation:animation forKey:nil];
                
            }];
        }

    }];
    
    if ([self selectedTab] == STUserHeaderTabStamps) {
        [self.stamps reloadData];
    }
    
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return [self.stamps isEmpty] && [self selectedTab] == STUserHeaderTabStamps;
}

- (void)setupNoDataView:(NoDataView*)view {
    
    CGRect frame = view.frame;
    CGFloat height = self.tableView.tableHeaderView.bounds.size.height;
    frame.origin.y = height;
    frame.size.height -= height;
    view.frame = frame;
    [view setupWithTitle:@"No stamps" detailTitle:[NSString stringWithFormat:@"No stamps found for %@.", (self.user==nil) ? @"this user" : self.user.screenName]];

}

@end
