//
//  PostStampViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampViewController.h"
#import "STStampDetailViewController.h"
#import "PostStampGraphView.h"
#import "PostStampHeaderView.h"
#import "STStampContainerView.h"
#import "STUsersViewController.h"
#import "PostStampBadgeTableCell.h"
#import "PostStampFriendsTableCell.h"
#import "STUserViewController.h"
#import "PostStampedByView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "PostStampShareView.h"
#import "STBlockUIView.h"
#import "Util.h"
#import "STStampedAPI.h"
#import "QuartzUtils.h"
#import "STNavigationItem.h"

@interface PostStampViewController ()
@property(nonatomic,strong) PostStampHeaderView *headerView;
@property(nonatomic,strong) PostStampGraphView *graphView;
@property(nonatomic,strong) PostStampedByView *stampedByView;
@property(nonatomic,strong) id<STStamp> stamp;
@property(nonatomic,strong) id<STUserDetail> user;
@property(nonatomic,strong) id<STStampedBy> stampedBy;
@property(nonatomic,strong) NSArray *badges;
@property(nonatomic,assign) BOOL firstBadge;
@end

@implementation PostStampViewController
@synthesize graphView=_graphView;
@synthesize headerView=_headerView;
@synthesize stamp=_stamp;
@synthesize user=_user;
@synthesize stampedByView=_stampedByView;
@synthesize badges=_badges;
@synthesize firstBadge;
@synthesize stampedBy = _stampedBy;


- (id)initWithStamp:(id<STStamp>)stamp {
    if ((self = [super initWithStyle:UITableViewStylePlain])) {
        self.title = NSLocalizedString(@"Your Stamp", @"Your Stamp");
        _stamp = [stamp retain];
        
        if (_stamp.badges.count) {
            
            NSMutableArray *array = [NSMutableArray array];
            
            for (id <STBadge> badge in _stamp.badges) {
                if ([badge.genre isEqualToString:@"entity_first_stamp"]) {
                    [array addObject:badge];
                    self.firstBadge = YES;
                }  else if ([badge.genre isEqualToString:@"user_first_stamp"]) {
                    [array addObject:badge];
                }
            }
            
            self.badges = array;
            
        } else {
            
            self.badges = [NSArray array];
            
        }
        
    }
    return self;
}

- (void)dealloc {
    self.headerView = nil;
    self.graphView = nil;
    self.user = nil;
    self.stamp = nil;
    self.stampedBy = nil;
    self.stampedByView = nil;
    self.badges = nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    self.tableView.rowHeight = 160.0f;
    self.tableView.contentInset = UIEdgeInsetsMake(0.0f, 0.0f, 20.0f, 0.0f);
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.99f green:0.99f blue:0.99f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    if (!_headerView) {
        PostStampHeaderView *view = [[PostStampHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 58.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableHeaderView = view;
        _headerView = [view retain];
        _headerView.titleLabel.text = self.stamp.entity.title;
        [view release];
    }
    
    if (!_stampedByView) {
        PostStampedByView *view = [[PostStampedByView alloc] initWithFrame:CGRectMake(0.0f, 20.0f, self.tableView.bounds.size.width, 85.0f)];
        view.delegate = (id<PostStampedByViewDelegate>)self;
        self.stampedByView = view;
        [view release];        
    }
    
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];
    [self reloadDataSource];
    
}

- (void)viewDidUnload {
    self.stampedByView = nil;
    self.graphView = nil;
    [super viewDidUnload];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


#pragma mark - Actions

- (void)done:(id)sender {
    [[Util sharedNavigationController] popToRootViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (void)resetContainer {
    
    if (!_tvContainer) {
        STStampContainerView *view = [[STStampContainerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, [self.tableView rectForSection:0].size.height)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self.tableView addSubview:view];
        [view release];
        _tvContainer = view;
    }
    
    [self.tableView sendSubviewToBack:_tvContainer];
    _tvContainer.frame = CGRectMake(0.0f, self.tableView.tableHeaderView.bounds.size.height + 4.0f, self.tableView.bounds.size.width, [self.tableView rectForSection:0].size.height + 6.0f);
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.row == 0) {
        return 150.0f;
    }
    
    if (indexPath.row <= self.badges.count) {
        return 76.0f;
    }
    
    return 105.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    NSInteger count = self.badges.count + 1;
    
    if (self.stampedBy) {
        count+=1;
    }
    
    return count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.row == 0) {
        
        [self resetContainer];
        
        static NSString *CellIdentifier = @"CellIdentifier";
        UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            
            cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil] autorelease];
            cell.layer.zPosition = 10;
            
            PostStampGraphView *graphView = [[PostStampGraphView alloc] initWithFrame:CGRectMake(0.0f, 10.0f, self.view.bounds.size.width, 140.0f)];
            if (self.stamp) {
                graphView.category = self.stamp.entity.category;
            }
            if (self.user) {
                graphView.user = self.user;
            } else {
                [graphView setLoading:YES];
            }
            [cell addSubview:graphView];
            self.graphView = graphView;
            [graphView release];  
            
        }
        return cell;
        
    }
    
    if (indexPath.row <= self.badges.count) {
        
        static NSString *BadgeCellIdentifier = @"BadgeCellIdentifier";
        PostStampBadgeTableCell *cell = [tableView dequeueReusableCellWithIdentifier:BadgeCellIdentifier];
        if (cell == nil) {
            cell = [[[PostStampBadgeTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:BadgeCellIdentifier] autorelease];
            cell.delegate = (id<PostStampBadgeTableCell>)self;
            cell.layer.zPosition = 10;
        }
        
        [cell showShadow:(indexPath.row==1)];
        [cell setupWithBadge:[self.badges objectAtIndex:indexPath.row-1]];
        
        return cell;
        
    }
    
    static NSString *FriendsCellIdentifier = @"FriendsCellIdentifier";
    PostStampFriendsTableCell *cell = [tableView dequeueReusableCellWithIdentifier:FriendsCellIdentifier];
    if (cell == nil) {
        cell = [[[PostStampFriendsTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:FriendsCellIdentifier] autorelease];
        cell.layer.zPosition = 10;
        cell.delegate = (id<PostStampFriendsTableCellDelegate>)self;
    }
    
    [cell showShadow:(indexPath.row==1)];
    [cell setupWithStampedBy:self.stampedBy andStamp:self.stamp];
    
    return cell;
    
}


#pragma mark - PostStampBadgeTableCell

- (void)postStampBadgeTableCellShare:(PostStampBadgeTableCell*)cell {
    
    PostStampShareView *view = [[PostStampShareView alloc] initWithFrame:self.view.bounds];
    view.layer.zPosition = 100;
    [self.view addSubview:view];
    [view popIn];
    [view release];
    
}


#pragma mark - PostStampFriendsTableCellDelegate

- (void)postStampFriendTableCell:(PostStampFriendsTableCell*)cell selectedStamp:(id<STStamp>)stamp {
    
    /*
    STUserViewController *controller = [[STUserViewController alloc] initWithUser:user];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
     */
    
    STActionContext* context = [STActionContext contextInView:self.view];
    id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];

    
}


#pragma mark - PostStampedByViewDelegate

- (void)postStampedByView:(PostStampedByView*)view selectedPreview:(id<STStampPreview>)item {
    
    // STStampDetailViewController *controller = [[[STStampDetailViewController alloc] initWithStamp:item.stamp] autorelease];
    
    STActionContext* context = [STActionContext contextInView:self.view];
    id<STAction> action = [STStampedActions actionViewStamp:item.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    
}

- (void)postStampedByView:(PostStampedByView*)view selectedAll:(id)sender {
    
    NSMutableArray *userIDs = [NSMutableArray array];
    NSMutableDictionary* stamps = [NSMutableDictionary dictionary];
    for (id<STStampPreview> preview in [self.stampedBy.everyone stampPreviews]) {
        NSString *userID = preview.user.userID;
        NSString* stampID = preview.stampID;
        if (userID && stampID) {
            [userIDs addObject:userID];
            [stamps setObject:stampID forKey:userID];
        }
    }
    STUsersViewController *controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
    controller.userIDToStampID = stamps;
    [self.navigationController pushViewController:controller animated:YES];
    
}


#pragma mark - Datasource

- (void)reloadDataSource {
    
    id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
    [[STStampedAPI sharedInstance] userDetailForUserID:user.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
        if (!error) {
            self.user = userDetail;
            [self.graphView setUser:self.user];
        } else {
            [self.graphView setLoading:YES];
        }
        [self resetContainer];
    }];
    
    if (!self.stamp || self.firstBadge) return; // ignore stamped by if the user is the first to stamp
    
    [[STStampedAPI sharedInstance] stampedByForEntityID:self.stamp.entity.entityID andCallback:^(id<STStampedBy> stampedBy, NSError *error, STCancellation *cancellation) {
        
        if (stampedBy) {
            
            self.stampedBy = stampedBy;
            
            if (_stampedByView && _stampedBy.everyone.count.integerValue > 0) {
                UIView *container = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, 110.0f)];
                container.backgroundColor = [UIColor clearColor];
                self.tableView.tableFooterView = container;
                [container addSubview:self.stampedByView];
                [container release];
                self.stampedByView.stampedBy = stampedBy;
            } 
            
            [self.tableView beginUpdates];
            [self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:self.badges.count+1 inSection:0]] withRowAnimation:UITableViewRowAnimationFade];
            [self resetContainer];
            [self.tableView endUpdates];
            [self resetContainer];
            
            NSLog(@"stampedby:%@", stampedBy);
            self.stampedBy = stampedBy;
            
        }
    }];
    
}





@end
