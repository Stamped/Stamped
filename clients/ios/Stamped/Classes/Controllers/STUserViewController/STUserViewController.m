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
#import "STEditProfileViewController.h"

#import "STDetailTableCell.h"
#import "STDescriptionTableCell.h"
#import "STTableViewSectionBackground.h"
#import "STCache.h"
#import "STGenericCacheConfiguration.h"
#import "STInboxPageSource.h"
#import "STSharedCaches.h"
#import "Util.h"
#import "STNavigationItem.h"
#import "STEvents.h"
#import "NoDataUtil.h"

#import "STStampsViewController.h"

@interface STUserViewController ()

@property (nonatomic, readonly, assign) BOOL loadingUser;
@property (nonatomic, readonly, retain) STCache* stampCache;
@property (nonatomic, readwrite, retain) STCacheSnapshot* stampSnapshot;
@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readwrite, copy) NSString *userIdentifier;
@property (nonatomic, retain, readonly) STUserGraphView *graphView;
@property (nonatomic, retain, readonly) UITableView *infoTableView;
@property (nonatomic, readwrite, retain) STCancellation* stampCacheCreationCancellation;
@property (nonatomic, readwrite, assign) BOOL loadingStamps;
@property (nonatomic, readwrite, retain) STUserHeaderView* headerView;


@end

@implementation STUserViewController
@synthesize userIdentifier;
@synthesize user = _user;
@synthesize graphView = _graphView;
@synthesize stampCache = _stampCache;
@synthesize stampSnapshot = _stampSnapshot;
@synthesize loadingUser = _loadingUser;
@synthesize infoTableView = _infoTableView;
@synthesize stampCacheCreationCancellation = _stampCacheCreationCancellation;
@synthesize loadingStamps = _loadingStamps;
@synthesize headerView = _headerView;

- (void)commonInit {
    
    _sectionViews = [[NSMutableArray alloc] initWithObjects:[NSNull null], [NSNull null], nil];
    _infoDataSource = [[NSArray array] retain];
    _loadingStamps = YES;
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheUpdate:) name:STCacheDidChangeNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheWillLoadPage:) name:STCacheWillLoadPageNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheDidLoadPage:) name:STCacheDidLoadPageNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(userUpdated:) name:STStampedAPIUserUpdatedNotification object:nil];
    
}

- (void)userUpdated:(id)notImportant {
    if (IS_CURRENT_USER(self.user.userID)) {
        self.user = [STStampedAPI sharedInstance].currentUser;
        NSLog(@"Updated profile");
        [self reloadDataSource];
        [self.headerView setupWithUser:self.user];
    }
}

- (void)handleStampCache:(STCache*)cache error:(NSError*)error cancellation:(STCancellation*)cancellation {
    self.stampCacheCreationCancellation = nil;
    if (cache) {
        _stampCache = [cache retain];
        self.stampSnapshot = _stampCache.snapshot;
    }
    [self reloadDataSource];
    [self reloadTableView:NO];
}

- (id)initWithUserIdentifier:(NSString*)identifier {
    
    if ((self = [super init])) {
        self.userIdentifier = identifier;
        [self commonInit];
    }
    return self;
    
}

- (id)initWithUser:(id<STUser>)user {
    
    if (self = [super init]) {
        _user = [user retain];
        self.userIdentifier = user.userID;
        //self.title = user.screenName;
        [self commonInit];
        
    }
    return self;
    
}

- (void)dealloc {
    [_headerView release];
    [_stampCacheCreationCancellation cancel];
    [_stampCacheCreationCancellation release];
    [STEvents removeObserver:self];
    if (_graphView) {
        [_graphView release], _graphView=nil;
    }
    self.userIdentifier = nil;
    [_user release], _user = nil;    
    
    [_stampCache saveWithAccelerator:nil andCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        //Nothing 
    }];
    [_stampSnapshot release];
    [_stampCache release];
    [_sectionViews release], _sectionViews=nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    self.tableView.showsVerticalScrollIndicator = NO;
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
        self.headerView = view;
    }
    
    if (LOGGED_IN && IS_CURRENT_USER(self.userIdentifier)) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Edit" style:UIBarButtonItemStyleBordered target:self action:@selector(editProfile:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
    }
    STGenericCacheConfiguration* config = [[[STGenericCacheConfiguration alloc] init] autorelease];
    config.pageSource = [[[STInboxPageSource alloc] initWithUserID:self.userIdentifier] autorelease];
    NSString* name = [NSString stringWithFormat:@"ProfileStamps_%@", self.userIdentifier];
    if ([[STStampedAPI sharedInstance].currentUser.userID isEqualToString:self.userIdentifier]) {
        self.stampCacheCreationCancellation = [STSharedCaches cacheForInboxScope:STStampedAPIScopeYou
                                                                    withCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
                                                                        [self handleStampCache:cache error:error cancellation:cancellation]; 
                                                                    }];
    }
    else {
        self.stampCacheCreationCancellation = [STCache cacheForName:name 
                                                        accelerator:nil
                                                      configuration:config
                                                        andCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
                                                            [self handleStampCache:cache error:error cancellation:cancellation];
                                                        }];
    }
    [self reloadDataSource];
    
    if (!_infoTableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStyleGrouped];
        if (tableView.backgroundView) {
            tableView.backgroundView.hidden = YES;
        }
        tableView.backgroundColor = [UIColor whiteColor];
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        _infoTableView = [tableView retain];
        [tableView release];
        _infoTableView.hidden = YES;
        
    }    
    
}

- (void)viewDidUnload {    
    [super viewDidUnload];
}


- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    if (_user && [self.navigationController.navigationBar isKindOfClass:[STNavigationBar class]] && [_user respondsToSelector:@selector(primaryColor)]) {
        [(STNavigationBar*)self.navigationController.navigationBar showUserStrip:YES forUser:_user];
    }
    
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    
    if ([self.navigationController.navigationBar isKindOfClass:[STNavigationBar class]]) {
        [(STNavigationBar*)self.navigationController.navigationBar showUserStrip:NO forUser:nil];
    }
    
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
    
    STEditProfileViewController *controller = [[[STEditProfileViewController alloc] init] autorelease];
    [Util pushController:controller modal:YES animated:YES];
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
    
    
    if ([_user isKindOfClass:[STSimpleUserDetail class]]) {
        
        STSimpleUserDetail *tempuser = (STSimpleUserDetail*)_user;
        
        NSMutableArray *dataSource = [[NSMutableArray alloc] init];
        if (IS_CURRENT_USER(self.userIdentifier)) {
            
            // stamps remaining count
            NSString *remaining = [NSString stringWithFormat:@"%i", [[tempuser numStampsLeft] integerValue]];
            [dataSource addObject:[NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:remaining, @"detail", @"Stamps remaining", @"title", @"STDetailTableCell", @"class", nil]]];
            
        }
        
        NSMutableArray *array = [[NSMutableArray alloc] init];
        NSDictionary *dictionary = nil;
        
        // bio
        if (tempuser.bio && tempuser.bio.length > 0) {
            dictionary = [NSDictionary dictionaryWithObjectsAndKeys:tempuser.bio, @"detail", @"About", @"title", @"STDescriptionTableCell", @"class", nil];
            [array addObject:dictionary];
        }
        
        // web profile
        dictionary = [NSDictionary dictionaryWithObjectsAndKeys:[NSString stringWithFormat:@"stamped.com/%@", tempuser.screenName] , @"detail", @"Web Profile", @"title", @"STDetailTableCell", @"class", nil];
        [array addObject:dictionary];
        
        // followers
        NSString *value = [NSString stringWithFormat:@"%i", [[tempuser numFollowers] integerValue]];
        dictionary = [NSDictionary dictionaryWithObjectsAndKeys:value, @"detail", @"Followers", @"title", @"STDetailTableCell", @"class", nil];
        [array addObject:dictionary];
        
        // following
        value = [NSString stringWithFormat:@"%i", [[tempuser numFriends] integerValue]];
        dictionary = [NSDictionary dictionaryWithObjectsAndKeys:value, @"detail", @"Following", @"title", @"STDetailTableCell", @"class", nil];
        [array addObject:dictionary];
        [dataSource addObject:array];
        
        [_infoDataSource release], _infoDataSource=nil;
        _infoDataSource = [dataSource retain];
        
        [array release];
        [dataSource release];
        [self.infoTableView reloadData];
        
    }
    
    
}

- (void)setLoading:(BOOL)loading {
    
    
    
}


#pragma mark - STUserHeaderViewDelegate

- (void)stUserHeaderViewAvatarTapped:(STUserHeaderView*)view {
    
    STPhotoViewController *controller = [[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:[Util largeProfileImageURLWithUser:self.user]]];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    [controller release];
    
}

- (void)stUserHeaderView:(STUserHeaderView*)view selectedTab:(STUserHeaderTab)tab {
    
    CGPoint offset = self.tableView.contentOffset;
    if (tab != STUserHeaderTabInfo) {
        if (self.tableView.tableHeaderView==nil && _infoTableView.tableHeaderView!=nil) {
            offset = self.infoTableView.contentOffset;
            UIView *header = [self.infoTableView.tableHeaderView retain];
            self.infoTableView.tableHeaderView = nil;
            self.tableView.tableHeaderView = header;
            [header release];
        }        
    }
    
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
        
        CGPoint offset = self.tableView.contentOffset;
        UIView *header = [self.tableView.tableHeaderView retain];
        self.tableView.tableHeaderView = nil;
        _infoTableView.tableHeaderView = header;
        [_infoTableView reloadData];
        [header release];
        self.infoTableView.contentOffset = offset;
        
    } else {
        
        UIView *header = [self.tableView.tableHeaderView retain];
        self.tableView.tableHeaderView = nil;
        self.tableView.tableHeaderView = header;
        [header release];
        
    }
    
    [self.tableView reloadData];
    self.tableView.contentOffset = offset;
    
    if (_infoTableView) {
        _infoTableView.hidden = (tab != STUserHeaderTabInfo);
    }
    
    if (self.graphView) {
        self.graphView.hidden = (tab != STUserHeaderTabGraph);
    }
    
    [self dataSourceDidFinishLoading];
    
}

- (void)stUserHeaderView:(STUserHeaderView*)view selectedStat:(STUserHeaderStat)stat {
    
    switch (stat) {
        case STUserHeaderStatCredit:
            [STStampsViewController creditsViewWithUserID:self.userIdentifier
                                              andCallback:^(UIViewController *controller, NSError *error, STCancellation *cancellation) {
                                                  [Util compareAndPushOnto:self withController:controller modal:NO animated:YES]; 
                                              }];
            
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


#pragma mark - STDescriptionTableCellDelegate

- (void)stDescriptionTableCell:(STDescriptionTableCell*)cell didExpand:(BOOL)expanded {
    
    _expanded = expanded;
    [self.infoTableView beginUpdates];
    cell.expanded = _expanded;
    [self.infoTableView endUpdates];
    [self setupSectionAtIndex:0];
    
}


#pragma mark - Section Styling

- (void)setupSectionAtIndex:(NSInteger)index {
    
    UIView *view = [_sectionViews objectAtIndex:index];
    
    if ([view isEqual:[NSNull null]]) {
        
        STTableViewSectionBackground *background = [[STTableViewSectionBackground alloc] initWithFrame:CGRectMake(12.0f, 0.0f, self.tableView.bounds.size.width-24.0f, 0.0f)];
        [self.infoTableView insertSubview:background atIndex:0];
        [_sectionViews replaceObjectAtIndex:index withObject:background];
        [background release];
        view = background;
        
    }
    
    CGRect frame = view.frame;
    frame.size.height = [self.infoTableView rectForSection:index].size.height;
    frame.origin.y = [self.infoTableView rectForSection:index].origin.y;    
    frame.origin.y += 8.0f;
    frame.size.height -= 16.0f;
    
    view.frame = frame;
    [self.infoTableView sendSubviewToBack:view];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView == _infoTableView) {
        
        NSArray *section = [_infoDataSource objectAtIndex:indexPath.section];
        NSDictionary *dictionary = [section objectAtIndex:indexPath.row];
        if ([[dictionary objectForKey:@"class"] isEqualToString:@"STDescriptionTableCell"]) {
            return [STDescriptionTableCell heightForText:[dictionary objectForKey:@"detail"] expanded:_expanded];
        }
        
        return 40.0f;
        
    }
    
    id<STStamp> stamp = [self.stampSnapshot objectAtIndex:indexPath.row];
    return [STStampCell heightForStamp:stamp];
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
    
    if (tableView == _infoTableView) {
        return [_infoDataSource count];
    }
    
    if ([self selectedTab] != STUserHeaderTabStamps) return 0;
    return self.stampSnapshot.count == 0 ? 0 : 1;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    if (tableView == _infoTableView) {
        NSArray *array = [_infoDataSource objectAtIndex:section];
        return [array count];
    }
    
    return self.stampSnapshot.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView == _infoTableView) {
        
        if (indexPath.row == 0) {
            [self setupSectionAtIndex:indexPath.section];
        }
        
        NSArray *section = [_infoDataSource objectAtIndex:indexPath.section];
        NSDictionary *dictionary = [section objectAtIndex:indexPath.row];
        
        if ([[dictionary objectForKey:@"class"] isEqualToString:@"STDescriptionTableCell"]) {
            
            static NSString *DetailCellIdentifier = @"DecriptionIdentifier";
            STDescriptionTableCell *cell = [tableView dequeueReusableCellWithIdentifier:DetailCellIdentifier];
            if (cell == nil) {
                cell = [[[STDescriptionTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:DetailCellIdentifier] autorelease];
                cell.delegate = (id<STDescriptionTableCellDelegate>)self;
                cell.layer.zPosition = 10;
            }
            [cell setFirst:YES last:NO];
            
            cell.titleLabel.text = [dictionary objectForKey:@"title"];
            cell.detailTitleLabel.text = [dictionary objectForKey:@"detail"];
            
            return cell;
            
        }
        
        
        static NSString *CellIdentifier = @"DetailIdentifier";
        STDetailTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            cell = [[[STDetailTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
            cell.layer.zPosition = 10;
        }
        
        [cell setFirst:(indexPath.row==0) last:(indexPath.row==[section count]-1)];
        cell.titleLabel.text = [dictionary objectForKey:@"title"];
        cell.detailTitleLabel.text = [dictionary objectForKey:@"detail"];
        
        if ([cell.titleLabel.text isEqualToString:@"Web Profile"]) {
            cell.detailTitleLabel.textColor = [UIColor colorWithRed:0.478f green:0.611f blue:0.8f alpha:1.0f];
        } else {
            cell.detailTitleLabel.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        }
        
        return cell;
        
    }
    
    
    static NSString *CellIdentifier = @"CellIdentifier";
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.delegate = (id<STStampCellDelegate>)self;
        cell.layer.zPosition = 10;
    }
    
    id<STStamp> stamp = [self.stampSnapshot objectAtIndex:indexPath.row];
    [cell setupWithStamp:stamp];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView == _infoTableView) {
        [tableView deselectRowAtIndexPath:indexPath animated:YES];
        
        NSArray *section = [_infoDataSource objectAtIndex:indexPath.section];
        NSDictionary *dictionary = [section objectAtIndex:indexPath.row];
        if ([[dictionary objectForKey:@"title"] isEqualToString:@"Web Profile"]) {
            
            UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:[dictionary objectForKey:@"detail"] delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:@"Cancel" destructiveButtonTitle:nil otherButtonTitles:@"Copy Link", @"Email Link", nil];
            actionSheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
            [actionSheet showInView:self.view];
            [actionSheet release];
            
        }
        return;
    }
    
    
    id<STStamp> stamp = [self.stampSnapshot objectAtIndex:indexPath.row];
    STActionContext *context = [STActionContext context];
    context.stamp = stamp;
    id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    
}


#pragma mark - STStampCellDelegate

- (void)stStampCellAvatarTapped:(STStampCell*)cell {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    id<STStamp> stamp = [self.stampSnapshot objectAtIndex:indexPath.row];
    STUserViewController *controller = [[STUserViewController alloc] initWithUser:stamp.user];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
}


#pragma mark - STEditProfileViewControllerDelegate

- (void)stEditProfileViewControllerCancelled:(STEditProfileViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}

- (void)stEditProfileViewControllerSaved:(STEditProfileViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return self.loadingStamps || _loadingUser;
}

- (void)loadNextPage {
    [self.stampCache refreshAtIndex:self.stampSnapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return self.stampCache.hasMore && [self selectedTab] == STUserHeaderTabStamps;
}

- (void)reloadDataSource {
    if ([self selectedTab] == STUserHeaderTabStamps) {
        [self.stampCache refreshAtIndex:-1 force:YES];
    }
    
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
    
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.stampSnapshot.count == 0 && [self selectedTab] == STUserHeaderTabStamps;
}

- (void)setupNoDataView:(NoDataView*)view {
    
    view.custom = YES;
    
    UIView* waterMark = [NoDataUtil stampWatermarkWithTitle:@"No stamps" andSubtitle:[NSString stringWithFormat:@"from %@", (self.user==nil) ? @"this user" : self.user.screenName]];
    waterMark.frame = [Util centeredAndBounded:waterMark.frame.size inFrame:CGRectMake(0, 0, view.frame.size.width, 160)];
    [view addSubview:waterMark];
    
//    CGRect frame = view.frame;
//    CGFloat height = self.tableView.tableHeaderView.bounds.size.height;
//    frame.origin.y = height;
//    frame.size.height -= height;
//    view.frame = frame;
//    [view setupWithTitle:@"No stamps" detailTitle:[NSString stringWithFormat:@"No stamps found for %@.", (self.user==nil) ? @"this user" : self.user.screenName]];
    
}
#pragma mark - Cache Methods

- (void)reloadTableView:(BOOL)preserveOffset {
    
    if (preserveOffset) {
        
        CGPoint offset = self.tableView.contentOffset;
        [self.tableView reloadData];
        self.tableView.contentOffset = offset;
        
    } else {
        [self.tableView reloadData];
    }
    
}

- (void)cacheWillLoadPage:(NSNotification *)notification {
    self.loadingStamps = YES;
    //[self.tableView reloadData];
}

- (void)cacheDidLoadPage:(NSNotification *)notification {
    self.loadingStamps = NO;
    [self dataSourceDidFinishLoading];
    //[self.tableView reloadData];
}

- (void)cacheUpdate:(NSNotification *)notification {
    if (self.stampCache) {
        self.stampSnapshot = self.stampCache.snapshot;
        [self reloadTableView:YES];
    }
}

@end
