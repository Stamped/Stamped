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


@implementation FindFriendsViewController

- (id)init {
    if ((self = [super initWithType:FriendsRequestTypeSuggested])) {
        self.title = @"Add Friends";
    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithWhite:0.0f alpha:0.05f];
    self.showsSearchBar = YES;
    [self.searchView setPlaceholderTitle:@"Search users"];
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
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


#pragma mark - FindFriendsHeaderViewDelegate

- (void)showFriendsControllerWithType:(FindFriendsSelectionType)type {
    
    FriendsViewController *controller = [[FriendsViewController alloc] initWithType:type];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    
}

- (void)findFriendsHeaderView:(FindFriendsHeaderView*)view selectedType:(FindFriendsSelectionType)type {
    
    if (type == FindFriendsSelectionTypeContacts) {
        
        UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Allow Stamped to access your Address Book?" message:@"Contacts are sent securly and never stored." delegate:(id<UIAlertViewDelegate>)self cancelButtonTitle:@"Don't Allow" otherButtonTitles:@"OK", nil];
        [alert show];
        [alert release];
        
    } else {
        
        [self showFriendsControllerWithType:type];
        
    }

}


#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (alertView.cancelButtonIndex==buttonIndex) return;

    [self showFriendsControllerWithType:FindFriendsSelectionTypeContacts];

}

@end
