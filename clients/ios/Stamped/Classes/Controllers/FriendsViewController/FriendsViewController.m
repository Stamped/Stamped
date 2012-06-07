//
//  FriendsViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "FriendsViewController.h"
#import "STUserViewController.h"
#import "STNavigationItem.h"
#import "FriendTableCell.h"
#import "STTwitter.h"
#import "STFacebook.h"
#import "STWelcomeViewController.h"
#import "STSimpleUser.h"

@interface FriendsViewController ()
@property(nonatomic,retain,readonly) Friends *friends;
- (void)presentTwitterAccounts;
@end

@implementation FriendsViewController
@synthesize friends=_friends;

- (id)initWithType:(FriendsRequestType)type {
    if ((self = [super init])) {
        _friends = [[Friends alloc] init];
        _friends.requestType = type;
        
        [STEvents addObserver:self selector:@selector(friendsFinished:) event:EventTypeFriendsFinished identifier:[NSString stringWithFormat:@"friends-%i", type]];
        
        if (type == FriendsRequestTypeTwitter) {
            
            [STEvents addObserver:self selector:@selector(twitterAuthFinished:) event:EventTypeTwitterAuthFinished];
            [STEvents addObserver:self selector:@selector(twitterAuthFailed:) event:EventTypeTwitterAuthFailed];
            
        } else if (type == FriendsRequestTypeFacebook) {
            
            [STEvents addObserver:self selector:@selector(facebookAuthFinished:) event:EventTypeFacebookAuthFinished];
            [STEvents addObserver:self selector:@selector(facebookAuthFailed:) event:EventTypeFacebookAuthFailed];
            
        }
        
        switch (type) {
            case FriendsRequestTypeContacts:
                self.title = @"Contacts";
                break;
            case FriendsRequestTypeTwitter:
                self.title = @"Twitter";
                break;
            case FriendsRequestTypeFacebook:
                self.title = @"Facebook";
                break;
            case FriendsRequestTypeSuggested:
                self.title = @"Suggestions";
                break;
            default:
                break;
        }
        
    }
    return self;
}

- (void)dealloc {
    [STEvents removeObserver:self];
    [_friends release], _friends=nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
        
    self.tableView.rowHeight = 64.0f;
    self.tableView.separatorColor = [UIColor colorWithWhite:0.0f alpha:0.05f];
    
    BOOL addDoneButton = NO;
    if (!self.navigationItem.rightBarButtonItem) {
        if (self.navigationController) {
            NSInteger index = [[self.navigationController viewControllers] indexOfObject:self];
            if (index > 0) {
                UIViewController *prevController = [[self.navigationController viewControllers] objectAtIndex:index-1];
                if ([prevController isKindOfClass:[STWelcomeViewController class]]) {
                    addDoneButton = YES;
                }
            }
        }
    }
    
    if (addDoneButton) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
    }
    
    _performingAuth = NO;
    if (_friends.requestType == FriendsRequestTypeFacebook) {
        
        if (![[STFacebook sharedInstance] isSessionValid]) {
            
            _performingAuth = YES;
            dispatch_after( dispatch_time(DISPATCH_TIME_NOW, 0.3f * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void) {
                
                [[STFacebook sharedInstance] auth];
                
            });
            
        }
         
    } else if (_friends.requestType == FriendsRequestTypeTwitter) {
        
        if (![[STTwitter sharedInstance] isSessionValid]) {
            
            _performingAuth = YES;
            dispatch_after( dispatch_time(DISPATCH_TIME_NOW, 0.3f * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void) {
                
                if (NSClassFromString(@"TWTweetComposeViewController") && [TWTweetComposeViewController canSendTweet]) {
                    [[STTwitter sharedInstance] requestAccess:^(BOOL granted) {
                        if (granted) {
                            [self presentTwitterAccounts];
                        } else {
                            _performingAuth = NO;
                            [self dataSourceDidFinishLoading];
                        }
                    }];
                } else {
                    
                    [[STTwitter sharedInstance] auth];
                    
                }
                
            });
        
        }
        
        
    } 
    
    
    [self reloadDataSource];
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Cell Animation

- (void)animateCell:(UITableViewCell*)cell withDelay:(float)delay {
    
    cell.layer.opacity = 0.0f;
    
    [CATransaction begin];
    [CATransaction setCompletionBlock:^{
        cell.layer.opacity = 1.0f;
        [cell.layer removeAllAnimations];
    }];
    
    CAAnimationGroup *animation = [CAAnimationGroup animation];
    animation.duration = 0.3f;
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut];
    animation.beginTime = [cell.layer convertTime:CACurrentMediaTime() fromLayer:nil] + delay;
    animation.removedOnCompletion = NO;
    animation.fillMode = kCAFillModeForwards;
    
    CABasicAnimation *position = [CABasicAnimation animationWithKeyPath:@"position"];
    position.fromValue = [NSValue valueWithCGPoint:CGPointMake(cell.layer.position.x, cell.layer.position.y + self.tableView.frame.size.height)];
    
    CAKeyframeAnimation *opacity = [CAKeyframeAnimation animationWithKeyPath:@"opacity"];
    opacity.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.0f], nil];
    opacity.keyTimes = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:0.01f], [NSNumber numberWithFloat:1.0f], nil];
    
    [animation setAnimations:[NSArray arrayWithObjects:position, opacity, nil]];
    [cell.layer addAnimation:animation forKey:nil];
    [CATransaction commit];
}

- (void)animateIn {
    
    float delay = 0.0f;
    for (UITableViewCell *cell in self.tableView.visibleCells) {
        if ([cell isKindOfClass:[FriendTableCell class]]) {
            [self animateCell:cell withDelay:delay];
            delay += 0.1f;
        }
    }
    
}


#pragma mark - Notifications

- (void)friendsFinished:(NSNotification*)notification {
    
    [self.tableView reloadData];
    [self dataSourceDidFinishLoading];
    [self animateIn];
    
}


#pragma mark - Twitter Notifications

- (void)twitterAuthFinished:(NSNotification*)notification {
    
    _performingAuth = NO;
    NSString *token = [[STTwitter sharedInstance] twitterToken];
    NSString *tokenSecret = [[STTwitter sharedInstance] twitterTokenSecret];
    _friends.requestParameters = [NSDictionary dictionaryWithObjectsAndKeys:token, @"user_token", tokenSecret, @"user_secret", nil];
    [self reloadDataSource];
    
}

- (void)twitterAuthFailed:(NSNotification*)notification {
    
    _performingAuth = NO;
    [self dataSourceDidFinishLoading];

}


#pragma mark - Facebook Notifications

- (void)facebookAuthFinished:(NSNotification*)notification {
    
    _performingAuth = NO;
    NSString *token = [[[STFacebook sharedInstance] facebook] accessToken];
    _friends.requestParameters = [NSDictionary dictionaryWithObject:token forKey:@"user_token"];
    [self reloadDataSource];
    
}

- (void)facebookAuthFailed:(NSNotification*)notification {
    
    _performingAuth = NO;
    [self dataSourceDidFinishLoading];

}


#pragma mark - Twitter Accounts Action Sheet

- (void)presentTwitterAccounts {
    
    UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:NSLocalizedString(@"Twitter Accounts", nil) delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:nil destructiveButtonTitle:nil otherButtonTitles:nil];
    
    for (ACAccount *account in [[STTwitter sharedInstance] accounts]) {
        [actionSheet addButtonWithTitle:account.username];
    }
    [actionSheet addButtonWithTitle:NSLocalizedString(@"Cancel", nil)];
    actionSheet.cancelButtonIndex = [actionSheet numberOfButtons] - 1;
    [actionSheet showInView:self.view];
    
}


#pragma mark - UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (actionSheet.cancelButtonIndex == buttonIndex) return;
    
    ACAccount *account = [[STTwitter sharedInstance] accountAtIndex:buttonIndex];
    [[STTwitter sharedInstance] reverseAuthWithAccount:account];
    
}


#pragma mark - Actions

- (void)done:(id)sender {
    
    [self.navigationController dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [_friends numberOfObjects];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    FriendTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[FriendTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier];
        cell.delegate = (id<FriendTableCellDelegate>)self;
    }
    
    id<STUser> user = [_friends objectAtIndex:indexPath.row];
    [cell setupWithUser:user];
    
    return cell;
    
}

- (NSString*)tableView:(UITableView*)tableView titleForHeaderInSection:(NSInteger)section {
    
    switch (_friends.requestType) {
        case FriendsRequestTypeFacebook:
            return @"Facebook friends on Stamped";
            break;
        case FriendsRequestTypeTwitter:
            return @"Twitter friends on Stamped";
            break;
        case FriendsRequestTypeContacts:
        case FriendsRequestTypeSuggested:
        default:
            return @"Friends on Stamped";
            break;
    }
    return nil;
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
    
    id<STUser> user = [_friends objectAtIndex:indexPath.row];
    STUserViewController *controller = [[STUserViewController alloc] initWithUser:user];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    
}


#pragma mark - FriendTableCellDelegate

- (void)friendTableCellToggleFollowing:(FriendTableCell*)cell {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    
    if (indexPath) {
        STSimpleUser *user = [_friends objectAtIndex:indexPath.row];
        [user toggleFollowing];
    }
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return [_friends isReloading] || _performingAuth;
}

- (void)loadNextPage {
    [_friends loadNextPage];
}

- (BOOL)dataSourceHasMoreData {
    return [_friends hasMore];
}

- (void)reloadDataSource {
    if (!_performingAuth) {
        [_friends reloadData];
    }
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return [_friends isEmpty];
}

- (void)setupNoDataView:(NoDataView*)view {
 
    NSString *string = @"";
    switch (_friends.requestType) {
        case FriendsRequestTypeContacts:
            string = @" from your Address Book";
            break;
        case FriendsRequestTypeTwitter:
            string = @" from Twitter";
            break;
        case FriendsRequestTypeFacebook:
            string = @" from Facebook";
            break;
        default:
            break;
    }
    
    [view setupWithTitle:@"No Friends" detailTitle:[NSString stringWithFormat:@"No friends found%@.", string]];
    
}

@end
