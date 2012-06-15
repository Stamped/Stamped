//
//  PostStampViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampViewController.h"
#import "PostStampGraphView.h"
#import "PostStampHeaderView.h"
#import "STStampContainerView.h"
#import "PostStampBadgeTableCell.h"
#import "PostStampFriendsTableCell.h"

@interface PostStampViewController ()
@property(nonatomic,strong) PostStampHeaderView *headerView;
@property(nonatomic,strong) PostStampGraphView *graphView;
@property(nonatomic,retain) id<STStamp> stamp;
@property(nonatomic,retain) id<STUserDetail> user;
@property(nonatomic,retain) id<STStampedBy> stampedBy;
@end

@implementation PostStampViewController
@synthesize graphView=_graphView;
@synthesize headerView=_headerView;
@synthesize stamp=_stamp;
@synthesize user=_user;


- (id)initWithStamp:(id<STStamp>)stamp {
    if ((self = [super initWithStyle:UITableViewStylePlain])) {
        self.title = NSLocalizedString(@"Your stamp", @"Your stamp");
        _stamp = [stamp retain];
    }
    return self;
}

- (void)dealloc {
    self.headerView = nil;
    self.graphView = nil;
    self.user = nil;
    self.stamp = nil;
    self.stampedBy = nil;
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
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
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
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];
    
    [self reloadDataSource];

}

- (void)viewDidUnload {
    self.graphView = nil;
    [super viewDidUnload];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


#pragma mark - Actions

- (void)done:(id)sender {
    
    [self dismissModalViewControllerAnimated:YES];
    
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
        return 140.0f;
    }
    
    if (self.stamp && self.stamp.badges && indexPath.row <= self.stamp.badges.count) {
        return 76.0f;
    }

    return 105.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    NSInteger count = 1;
    
    if (self.stamp) {
        count+=self.stamp.badges.count;
    }
    
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
            
            PostStampGraphView *graphView = [[PostStampGraphView alloc] initWithFrame:CGRectMake(0.0f, 10.0f, self.view.bounds.size.width, 130.0f)];
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
    
    if (self.stamp.badges && indexPath.row <= self.stamp.badges.count) {
        
        static NSString *BadgeCellIdentifier = @"BadgeCellIdentifier";
        PostStampBadgeTableCell *cell = [tableView dequeueReusableCellWithIdentifier:BadgeCellIdentifier];
        if (cell == nil) {
            cell = [[[PostStampBadgeTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:BadgeCellIdentifier] autorelease];
            cell.layer.zPosition = 10;
        }
        
        [cell showShadow:(indexPath.row==1)];
        if(self.stamp) {
            [cell setupWithBadge:[[self.stamp badges] objectAtIndex:indexPath.row-1]];
        }
        
        return cell;
        
    }
    
    static NSString *FriendsCellIdentifier = @"FriendsCellIdentifier";
    PostStampFriendsTableCell *cell = [tableView dequeueReusableCellWithIdentifier:FriendsCellIdentifier];
    if (cell == nil) {
        cell = [[[PostStampFriendsTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:FriendsCellIdentifier] autorelease];
        cell.layer.zPosition = 10;
    }
    
    [cell showShadow:(indexPath.row==1)];
    [cell setupWithStampedBy:self.stampedBy andStamp:self.stamp];
    
    return cell;
    
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
    }];
    
    if (!self.stamp) return;

    [[STStampedAPI sharedInstance] stampedByForEntityID:self.stamp.entity.entityID andCallback:^(id<STStampedBy> stampedBy, NSError *error, STCancellation *cancellation) {
        
        self.stampedBy = stampedBy;
        
        NSInteger count = 1;
        if (self.stamp) {
            count+=self.stamp.badges.count;
        }
        
        [self.tableView beginUpdates];
        [self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:count inSection:0]] withRowAnimation:UITableViewRowAnimationFade];
        [self resetContainer];
        [self.tableView endUpdates];
        [self resetContainer];

    }];
    
}





@end
