//
//  FindFriendsViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "FindFriendsViewController.h"
#import "FindFriendsHeaderView.h"
#import "FriendsViewController.h"
#import "STDebug.h"


@interface FindFriendsViewController ()

@property (nonatomic, readwrite, assign) BOOL firstAppearance;

@end

@implementation FindFriendsViewController

@synthesize firstAppearance = _firstAppearance;

- (id)init {
    if ((self = [super initWithType:FriendsRequestTypeSuggested])) {
        _firstAppearance = YES;
        self.title = @"Add Friends";
    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithWhite:0.0f alpha:0.05f];
    self.showsSearchBar = YES;
    [self.searchView setPlaceholderTitle:@"Search users"];
    //[Util addHomeButtonToController:self withBadge:YES];
    self.tableView.contentOffset = CGPointZero;
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
}

- (void)viewDidAppear:(BOOL)animated {
    
    [super viewDidAppear:animated];
        self.tableView.contentOffset = CGPointZero;
}

#pragma mark - Table view data source

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.section == 0) {
        return 180.0f;
    }
    
    return 64.0f;
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return [super numberOfSectionsInTableView:tableView] + 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) {
        return 1;
    }
    return [super tableView:tableView numberOfRowsInSection:section];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.section == 0) {
        
        UITableViewCell *cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil] autorelease];
        cell.selectionStyle = UITableViewCellSelectionStyleNone;
        
        FindFriendsHeaderView *view = [[FindFriendsHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 180.0f)];
        view.delegate = (id<FindFriendsHeaderViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [cell addSubview:view];
        [view release];
        
        return cell;
        
    }
    
    return [super tableView:tableView cellForRowAtIndexPath:indexPath];

}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (section == 1) {
        return [super tableView:tableView heightForHeaderInSection:section];
    }
    return 0.0f;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {

    if (section == 1) {
        return [super tableView:tableView viewForHeaderInSection:section];
    }
    return nil;
    
}

- (NSString*)tableView:(UITableView*)tableView titleForHeaderInSection:(NSInteger)section {
    if (section == 1) {
        return NSLocalizedString(@"Suggestions", @"Suggestions");
    }
    return nil;
}

#pragma mark - STSearchViewDelegate

- (void)stSearchViewHitSearch:(STSearchView*)view withText:(NSString*)text {
    FriendsViewController *controller = [[FriendsViewController alloc] initWithQuery:text];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
}


#pragma mark - FindFriendsHeaderViewDelegate

- (void)showFriendsControllerWithType:(FindFriendsSelectionType)type {
    
    FriendsViewController *controller = [[FriendsViewController alloc] initWithType:type];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    
}

- (void)findFriendsHeaderView:(FindFriendsHeaderView*)view selectedType:(FindFriendsSelectionType)type {
    
    if (type == FindFriendsSelectionTypeContacts) {
        
        UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Allow Stamped to access your Address Book?" 
                                                        message:@"Contacts are sent securely and never stored."
                                                       delegate:(id<UIAlertViewDelegate>)self
                                              cancelButtonTitle:@"Don't Allow" 
                                              otherButtonTitles:@"OK", nil];
        [alert show];
        [alert release];
        
    } 
    else {
        
        [self showFriendsControllerWithType:type];
        
    }

}


#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (alertView.cancelButtonIndex==buttonIndex) return;

    [self showFriendsControllerWithType:FindFriendsSelectionTypeContacts];

}

- (void)setValue:(id)value forUndefinedKey:(NSString *)key {
    NSLog(@"Swallowed bad key:%@ withValue:%@", key, value);
}

#pragma mark - STRestController Overrides

- (void)setupNoDataView:(NoDataView*)view {

    CGRect frame = view.frame;
    CGFloat height = [self.tableView rectForSection:0].size.height + self.tableView.tableHeaderView.bounds.size.height;
    frame.origin.y = height;
    frame.size.height -= height;
    view.frame = frame;
    [super setupNoDataView:view];
    
}


@end
