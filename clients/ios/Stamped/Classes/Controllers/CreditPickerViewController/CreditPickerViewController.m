//
//  CreditPickerViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "CreditPickerViewController.h"
#import "CreditHeaderView.h"
#import "CreditUserTableCell.h"

@interface CreditPickerViewController ()
@property(nonatomic,retain) CreditHeaderView *headerView;
@property(nonatomic,retain) id <STStampedByGroup> stampedByFriends;
@property(nonatomic,retain) NSArray *users;
@property(nonatomic,retain) NSString *entityIdentifier;
@property(nonatomic,retain) NSMutableArray *selectedUsers;
@property(nonatomic,assign) BOOL loadingUsers;
@end

@implementation CreditPickerViewController
@synthesize delegate;
@synthesize stampedByFriends=_stampedByFriends;
@synthesize users=_users;
@synthesize entityIdentifier=_entityIdentifier;
@synthesize loadingUsers=_loadingUsers;
@synthesize headerView=_headerView;

- (id)initWithEntityIdentifier:(NSString*)identifier {
    if ((self = [super init])) {

        self.title = @"Credit";
        _users = [[NSArray alloc] init];
        _selectedUsers = [[NSMutableArray alloc] init];
        
        _entityIdentifier = [identifier retain];
        id<STStampedBy> stampedBy = [[STStampedAPI sharedInstance] cachedStampedByForEntityID:identifier];
        _stampedByFriends = [stampedBy.friends retain];
        
    }
    return self;
}

- (void)dealloc {
    
    [_selectedUsers release], _selectedUsers=nil;
    [_entityIdentifier release], _entityIdentifier=nil;
    [_stampedByFriends release], _stampedByFriends=nil;
    [_users release], _users=nil;
    [super dealloc];
    
}

- (void)viewDidLoad {
    [super viewDidLoad];

    self.tableView.rowHeight = 64.0f;
    self.tableView.separatorColor = [UIColor colorWithWhite:0.0f alpha:0.05f];

    if (!_headerView) {
      
        CreditHeaderView *view = [[CreditHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 48.0f)];
        view.delegate = (id<CreditHeaderViewDelegate>)self;
        view.dataSource = (id<CreditHeaderViewDataSource>)self;
        [self.view addSubview:view];
        self.headerView = view;
        [view release];
        [self setContentInset:UIEdgeInsetsMake(self.headerView.bounds.size.height, 0, 0, 0)];
    }
    
    if (!self.navigationItem.leftBarButtonItem) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
        self.navigationItem.leftBarButtonItem = button;
        [button release];
        
    }
    
    if (!self.navigationItem.rightBarButtonItem) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Save", @"Save") style:UIBarButtonItemStyleDone target:self action:@selector(save:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
        
    }
    
    [self reloadDataSource];
 
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


#pragma mark - Actions

- (void)save:(id)sender {
    
    NSMutableArray *usernames = [[NSMutableArray alloc] initWithCapacity:self.selectedUsers.count];
    
    for (id <STUser> user in self.selectedUsers) {
    
        [usernames addObject:user.screenName];
    
    }
    
    if ([(id)delegate respondsToSelector:@selector(creditPickerViewController:doneWithUsernames:)]) {
        [self.delegate creditPickerViewController:self doneWithUsernames:usernames];
    }
    
    [usernames release];
    
}

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(creditPickerViewControllerCancelled:)]) {
        [self.delegate creditPickerViewControllerCancelled:self];
    } else {
        [self dismissModalViewControllerAnimated:YES];
    }

}


#pragma mark - CreditHeaderViewDelegate

- (void)creditHeaderViewDidBeginEditing:(CreditHeaderView*)view {

    
}

- (void)creditHeaderViewDidEndEditing:(CreditHeaderView*)view {
    
    [self.tableView setContentOffset:CGPointZero animated:YES];

}

- (void)creditHeaderViewFrameChanged:(CreditHeaderView*)view {

    [self setContentInset:UIEdgeInsetsMake(self.headerView.bounds.size.height, 0, 0, 0)];

}

- (void)creditHeaderView:(CreditHeaderView*)view textChanged:(NSString*)text {
        
}

- (void)creditHeaderView:(CreditHeaderView*)view adjustOffset:(CGPoint)offset {
    
    [self.tableView setContentOffset:offset animated:YES];

}


#pragma mark - CreditHeaderViewDataSource

- (NSInteger)creditHeaderViewNumberOfCells:(CreditHeaderView*)view {
    
    return [self.selectedUsers count];
    
}

- (CreditBubbleCell*)creditHeaderView:(CreditHeaderView*)view cellForIndex:(NSInteger)index {
        
    CreditBubbleCell *cell = [[[CreditBubbleCell alloc] initWithFrame:CGRectZero] autorelease];
    id<STUser> user = [self.selectedUsers objectAtIndex:index];
    cell.titleLabel.text = user.screenName;
    [cell.stampView setupWithUser:user];
    return cell;
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0 && [[_stampedByFriends count] integerValue] > 0) {
        return [[_stampedByFriends count] integerValue];
    }
    return [_users count];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    if ([[_stampedByFriends count] integerValue] > 0) {
        return 2;
    }
    
    return 1;
    
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    CreditUserTableCell *cell = (CreditUserTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[CreditUserTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    id <STUser> user = nil;
    
    if (indexPath.section == 0 && [[_stampedByFriends count] integerValue] > 0) {
        
        id <STStampPreview> preview = [_stampedByFriends.stampPreviews objectAtIndex:indexPath.row];
        user = preview.user;
        
    } else {
        
        user = [_users objectAtIndex:indexPath.row];
        
    }
    
    [cell setupWithUser:user];
    cell.checked = [self.selectedUsers containsObject:user];
    
    return cell;

}

- (NSString*)tableView:(UITableView*)tableView titleForHeaderInSection:(NSInteger)section {
 
    if (section == 0 && [[_stampedByFriends count] integerValue] > 0) {
        return @"Stamped by";
    }
    return @"People";
   
}
    
- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (![self tableView:tableView titleForHeaderInSection:section]) {
        return 0.0f;
    }
    return 25.0f;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    NSString *title = [self tableView:tableView titleForHeaderInSection:section];
    if (title) {
        
        UIImage *image = [UIImage imageNamed:@"find_friends_section_header_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, image.size.height)];
        imageView.image = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(10.0f, floorf((imageView.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.font = font;
        label.textColor = [UIColor whiteColor];
        label.backgroundColor = [UIColor clearColor];
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.2f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.text =  title;
        [imageView addSubview:label];
        [label sizeToFit];
        [label release];
        
        return [imageView autorelease];
        
    }
    
    return nil;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id <STUser> user = nil;
    
    if (indexPath.section == 0 && [[_stampedByFriends count] integerValue] > 0) {
        
        id <STStampPreview> preview = [_stampedByFriends.stampPreviews objectAtIndex:indexPath.row];
        user = preview.user;
        
    } else {
        
        user = [_users objectAtIndex:indexPath.row];

    }
    
    if ([self.selectedUsers containsObject:user]) {
        [self.selectedUsers removeObject:user];
    } else {
        [self.selectedUsers addObject:user];
    }
    
    CreditUserTableCell *cell = (CreditUserTableCell*)[tableView cellForRowAtIndexPath:indexPath];
    cell.checked = !cell.checked;
    
    [tableView deselectRowAtIndexPath:indexPath animated:YES];
    [self.headerView reloadData];
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return _loadingUsers;
}

- (void)loadNextPage {
}

- (BOOL)dataSourceHasMoreData {
    return NO;
}

- (void)reloadDataSource {
    if (!_entityIdentifier || _loadingUsers) return; 
    _loadingUsers = YES;
    
    id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
    [[STStampedAPI sharedInstance] friendIDsForUserID:user.userID andCallback:^(NSArray *friendIDs, NSError *error) {
                
        if (friendIDs) {
           
            [[STStampedAPI sharedInstance] userDetailsForUserIDs:friendIDs andCallback:^(NSArray<STUserDetail> *userDetails, NSError *error, STCancellation* cancellation) {
                
                if (userDetails) {
                    [_users release], _users = nil;
                    _users = [userDetails retain];
                }
                
                _loadingUsers = NO;
                [self.tableView reloadData];
                [self animateIn];
                [self dataSourceDidFinishLoading];
                
            }];
            
        } else {
            
            _loadingUsers = NO;
            [self.tableView reloadData];
            [self animateIn];
            [self dataSourceDidFinishLoading];

            
        }
      
    }];
    
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return [_users count] == 0 && [[_stampedByFriends count] integerValue] == 0;
}

- (void)setupNoDataView:(NoDataView*)view {
    
    CGRect frame = view.frame;
    CGFloat height = self.headerView.bounds.size.height;
    frame.origin.y = height;
    frame.size.height -= height;
    view.frame = frame;
    [view setupWithTitle:@"No Users" detailTitle:@"No users found."];
    
}

@end
