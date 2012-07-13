//
//  STLeftMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 
 2012.07.03: removed anchor view and consolidated settings and todo into main list.
 */

#import "STLeftMenuViewController.h"
#import "Util.h"
#import "STMenuController.h"
#import "DDMenuController.h"
#import "STUniversalNewsController.h"
#import "STTodoViewController.h"
#import "STDebugViewController.h"
#import "STRootViewController.h"
#import "STIWantToViewController.h"
#import "STInboxViewController.h"
#import "STConfiguration.h"
#import "LeftMenuTableCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STNavigationItem.h"
#import "STStampedAPI.h"
#import "STUser.h"
#import "STUserViewController.h"
#import "STAvatarView.h"
#import "STPlayer.h"
#import "STPlayerPopUp.h"
#import "STEvents.h"
#import "UIFont+Stamped.h"
#import "STAppDelegate.h"
#import "LeftMenuLargeCell.h"

#define kAvatarViewTag 101

static NSString* const _inboxNameKey = @"Root.inboxName";
static NSString* const _iWantToNameKey = @"Root.iWantToName";
static NSString* const _newsNameKey = @"Root.newsName";
static NSString* const _addFriendsNameKey = @"Root.addFriendsName";
static NSString* const _userNameKey = @"Root.userName";
static NSString* const _debugNameKey = @"Root.debugName";
static NSString* const _todoNameKey = @"Root.todoName";
static NSString* const _settingsNameKey = @"Root.settingsName";

@interface STLeftMenuViewController () <UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, readonly, retain) UITableView *tableView;
@property (nonatomic, readonly, retain) UIView* titleView;
@property (nonatomic, readonly, retain) UIView* playerView;
@property (nonatomic, readonly, retain) UILabel* playerTitleView;

@property (nonatomic, readwrite, retain) NSArray* dataSource;
@property (nonatomic, readwrite, retain) NSDictionary* controllerStore;
@property (nonatomic, readwrite, retain) NSIndexPath* selectedIndexPath;
@property (nonatomic, readwrite, retain) NSNumber* loggedIn;

@end

@interface STLeftMenuTopCell : UITableViewCell

@end

@implementation STLeftMenuViewController

@synthesize tableView=_tableView;
@synthesize titleView = _titleView;
@synthesize playerView = _playerView;
@synthesize playerTitleView = _playerTitleView;

@synthesize dataSource = _dataSource;
@synthesize controllerStore = _controllerStore;
@synthesize selectedIndexPath = _selectedIndexPath;
@synthesize loggedIn = _loggedIn;

- (id)init {
    if ((self = [super init])) {
        _selectedIndexPath = [[NSIndexPath indexPathForRow:0 inSection:0] retain];
        [self loginStatusChanged:nil];
        
    }
    return self;
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_tableView release];
    [_selectedIndexPath release];
    [_dataSource release];
    [_controllerStore release];
    [_titleView release];
    [_loggedIn release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    UITableView *tableView = [[[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStylePlain] autorelease];
    tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    tableView.rowHeight = 48.0f;
    tableView.scrollEnabled = NO;
    tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    tableView.delegate = (id<UITableViewDelegate>)self;
    tableView.dataSource = (id<UITableViewDataSource>)self;
    [self.view addSubview:tableView];
    _tableView = [tableView retain];
    
    UIImageView *imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]] autorelease];
    tableView.backgroundView = imageView;
    
    imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"left_logo.png"]] autorelease];
    UIView *view = [[[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 75.0f)] autorelease];
    [view addSubview:imageView];
    self.tableView.tableHeaderView = view;
    _titleView = imageView;
    
    _playerView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 100)];
    _playerTitleView = [[UILabel alloc] initWithFrame:CGRectMake(50, 0, 180, 70)];
    _playerTitleView.backgroundColor = [UIColor clearColor];
    _playerTitleView.textColor = [UIColor whiteColor];
    _playerTitleView.font = [UIFont stampedBoldFontWithSize:16];
    _playerTitleView.lineBreakMode = UILineBreakModeTailTruncation;
    
    UIButton* playerButton = [UIButton buttonWithType:UIButtonTypeCustom];
    [playerButton setImage:[UIImage imageNamed:@"menu_icon-viewplaylist"] forState:UIControlStateNormal];
    [playerButton addTarget:self action:@selector(showPlaylist:) forControlEvents:UIControlEventTouchUpInside];
    playerButton.frame = CGRectMake(10, 10, 30, 30);
    [_playerView addSubview:playerButton];
    [_playerView addSubview:_playerTitleView];
    [view addSubview:_playerView];
    
    CGRect frame = imageView.frame;
    frame.origin.x = 14.0f;
    frame.origin.y = (view.bounds.size.height-imageView.bounds.size.height)/2;
    imageView.frame = frame;
    
    UIImageView *corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_left.png"]];
    [self.view addSubview:corner];
    [corner release];
    
    corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_left.png"]];
    corner.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleRightMargin;
    corner.layer.transform = CATransform3DMakeScale(1.0f, -1.0f, 0.0f);
    [self.view addSubview:corner];
    [corner release];
    
    frame = corner.frame;
    frame.origin.y = (self.view.bounds.size.height-corner.bounds.size.height);
    corner.frame = frame;
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(configurationChanged:) name:STConfigurationValueDidChangeNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(loginStatusChanged:) name:STStampedAPILoginNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(loginStatusChanged:) name:STStampedAPILogoutNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(playerStateChanged:) name:STPlayerStateChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(playerItemChanged:) name:STPlayerItemChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(loginStatusChanged:) name:DDMenuControllerWillShowLeftMenuNotification object:nil];
    [self playerStateChanged:nil];
}

- (void)showPlaylist:(id)notImportant {
    [STPlayerPopUp present];
}

- (void)playerStateChanged:(id)notImportant {
    STPlayer* player = [STPlayer sharedInstance];
    if (player.paused) {
        _titleView.hidden = NO;
        _playerView.hidden = YES;
    }
    else {
        _playerView.hidden = NO;
        _titleView.hidden = YES;
        [self playerItemChanged:nil];
    }
}

- (void)playerItemChanged:(id)notImportant {
    STPlayer* player = [STPlayer sharedInstance];
    if (player.itemCount) {
        id<STPlaylistItem> item = [player itemAtIndex:player.currentItemIndex];
        _playerTitleView.text = item.name;
    }
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    
    if (_selectedIndexPath) {
        [self.tableView selectRowAtIndexPath:_selectedIndexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
    }
    
}


#pragma mark - Icon Helper

- (NSString*)iconTitleForTableView:(UITableView*)tableView atIndex:(NSInteger)index {
    switch (index) {
        case 0:
            return @"left_menu_icon_stamps.png";
            break;
        case 1:
            return @"left_menu_icon_guide";
            break;
        case 2:
            return @"left_menu_icon-activity";
            break;
        case 3:
            return @"left_menu_icon-todo";
            break;
        case 4:
            return @"left_menu_icon_addfriends";
            break;
        case 5:
            return @"left_unused";
            break;
        case 6:
            return @"left_menu_icon_settings.png";
            break;                
        default:
            break;
    }
    return nil;
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return self.dataSource.count;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.row < 2) {
        return 72;
    }
    return 48.0f;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.row < 2) {
        
        static NSString *CellIdentifier = @"CellIdentifier2";
        
        LeftMenuLargeCell *cell = (LeftMenuLargeCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            cell = [[[LeftMenuLargeCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
            cell.selectionStyle = UITableViewCellSelectionStyleNone;
            cell.delegate = (id<LeftMenuTableCellDelegate>)self;
        }
        
        [STEvents removeObserver:cell];
        cell.titleLabel.text = [STConfiguration value:[_dataSource objectAtIndex:indexPath.row]];
        cell.icon = [UIImage imageNamed:[self iconTitleForTableView:tableView atIndex:indexPath.row]];
        if (indexPath.row == 0) {
            NSString* c1 = @"004ab3";
            NSString* c2 = @"0055cc";
//            if (LOGGED_IN) {
//                c1 = [STStampedAPI sharedInstance].currentUser.primaryColor;
//                c2 = [STStampedAPI sharedInstance].currentUser.secondaryColor;
//                if (!c2) {
//                    c2 = c1;
//                }
//            }
            cell.icon = [Util gradientImage:cell.icon withPrimaryColor:c1 secondary:c2];
        }
        [cell setTop:(indexPath.row!=0) bottom:(indexPath.row<[_dataSource count]-1)];
        
        if ([cell.titleLabel.text isEqualToString:[STConfiguration value:_newsNameKey]]) {
            [STEvents addObserver:cell selector:@selector(countUpdated:) event:EventTypeUnreadCountUpdated];
            [cell countUpdated:nil];
        } 
        
        if ([indexPath isEqual:_selectedIndexPath]) {
            cell.selected = YES;
        }
        
            
            if ([cell viewWithTag:kAvatarViewTag]) {
                [[cell viewWithTag:kAvatarViewTag] removeFromSuperview];
            }
            
        return cell;
    }
    else {
        static NSString *CellIdentifier = @"CellIdentifier";
        
        LeftMenuTableCell *cell = (LeftMenuTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            cell = [[[LeftMenuTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
            cell.selectionStyle = UITableViewCellSelectionStyleNone;
            cell.delegate = (id<LeftMenuTableCellDelegate>)self;
        }
        
        [STEvents removeObserver:cell];
        cell.titleLabel.text = [STConfiguration value:[_dataSource objectAtIndex:indexPath.row]];
        cell.icon = [UIImage imageNamed:[self iconTitleForTableView:tableView atIndex:indexPath.row]];
        [cell setTop:(indexPath.row!=0) bottom:(indexPath.row<[_dataSource count]-1)];
        
        if ([cell.titleLabel.text isEqualToString:[STConfiguration value:_newsNameKey]]) {
            [STEvents addObserver:cell selector:@selector(countUpdated:) event:EventTypeUnreadCountUpdated];
            [cell countUpdated:nil];
        } 
        
        if ([indexPath isEqual:_selectedIndexPath]) {
            cell.selected = YES;
        }
        cell.whiteIcon = nil;
        if (indexPath.row == 2) {
            cell.whiteIcon = [UIImage imageNamed:@"left_menu_icon-activity_white"];
        }
        else if (indexPath.row == 3) {
            cell.whiteIcon = [UIImage imageNamed:@"left_menu_icon-todo_white"];
        }
        
        if (indexPath.row == 5 && LOGGED_IN) {
            
            // user row
            id<STUser> user = [[STStampedAPI sharedInstance] currentUser];
            cell.titleLabel.text = [user name];
            
            if (![cell viewWithTag:kAvatarViewTag]) {
                
                cell.icon = nil;
                
                STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(12.0f, (cell.bounds.size.height-24.0f)/2, 24.0f, 24.0f)];
                view.userInteractionEnabled = NO;
                view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
                [cell addSubview:view];
                view.imageURL = [NSURL URLWithString:[user imageURL]];
                
                view.backgroundView.layer.shadowOffset = CGSizeMake(0.0f, -1.0f);
                view.backgroundView.layer.shadowRadius = 0.0f;
                view.backgroundView.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.25f];
                
                [view release];
            }
            
        } else {
            
            if ([cell viewWithTag:kAvatarViewTag]) {
                [[cell viewWithTag:kAvatarViewTag] removeFromSuperview];
            }
            
        }
        
        return cell;
    }
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    
    if ( _selectedIndexPath && [_selectedIndexPath isEqual:indexPath]) {
        
        // controller is already root, lets just pop it to root like a tab bar
        STMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
        UINavigationController *navController = (UINavigationController*)[menuController rootViewController];
        if (navController && [navController isKindOfClass:[UINavigationController class]]) {
            [menuController showRootController:YES];
            [navController popToRootViewControllerAnimated:NO];
            return;
        }
        
    }
    
    NSString *key = [_dataSource objectAtIndex:indexPath.row];
    NSString *value = [_controllerStore objectForKey:key];
    
    UIViewController *controller = nil;
    
    if ([[STConfiguration value:value] isEqual:[STUserViewController class]]) {
        
        id user = [[STStampedAPI sharedInstance] currentUser];
        controller = [[STUserViewController alloc] initWithUser:(STSimpleUserDetail*)user];
        
    } else {
        
        controller = [[[STConfiguration value:value] alloc] init];
        
    }
    
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    STMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    
    [menuController setRootController:navController animated:YES];
    [Util addHomeButtonToController:controller withBadge:![controller isKindOfClass:[STUniversalNewsController class]]];
    
    [controller release];
    [navController release];
    
    
    if (![indexPath isEqual:_selectedIndexPath]) {
        UITableViewCell *cell = [self.tableView cellForRowAtIndexPath:_selectedIndexPath];
        [cell setSelected:NO];
    }
    
    [_selectedIndexPath release], _selectedIndexPath=nil;
    _selectedIndexPath = [indexPath retain];
    
    [self performSelector:@selector(loginStatusChanged:) withObject:nil afterDelay:.3];
}


#pragma mark - LeftMenuTableCellDelegate

- (void)leftMenuTableCellHighlighted:(UITableViewCell*)cell highlighted:(BOOL)highlighted {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    
    if (_selectedIndexPath) {
        if (![indexPath isEqual:_selectedIndexPath]) {
            UITableViewCell *selectedCell = [self.tableView cellForRowAtIndexPath:_selectedIndexPath];
            [selectedCell setSelected:!highlighted];
        }
    }
    
}


#pragma mark - Actions

- (void)done:(id)sender {
    
    UIViewController *controller = (id)((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - Configurations

+ (void)setupConfigurations {
    [STConfiguration addString:@"The Feed" forKey:_inboxNameKey];
    [STConfiguration addString:@"The Guide" forKey:_iWantToNameKey];
    [STConfiguration addString:@"Activity" forKey:_newsNameKey];
    [STConfiguration addString:@"Debug" forKey:_debugNameKey];
    [STConfiguration addString:@"To-Do" forKey:_todoNameKey];
    [STConfiguration addString:@"Settings" forKey:_settingsNameKey];
    [STConfiguration addString:@"Add Friends" forKey:_addFriendsNameKey];
    [STConfiguration addString:@"User" forKey:_userNameKey];
}

- (void)configurationChanged:(id)notImportant {
    [self.tableView reloadData];
}


- (void)reloadDataSource {
    [self loginStatusChanged:nil];
}

- (void)loginStatusChanged:(id)notImportant {
    
    BOOL currentStatus = LOGGED_IN;
    if (self.loggedIn && self.loggedIn.boolValue == currentStatus) return;
    self.loggedIn = [NSNumber numberWithBool:currentStatus];
    NSIndexPath* selection = self.tableView.indexPathForSelectedRow;
    [_dataSource release];
    [_controllerStore release];
    if (LOGGED_IN) {
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", _inboxNameKey,
                                    @"Root.iWantTo", _iWantToNameKey,
                                    @"Root.news", _newsNameKey,
                                    @"Root.findFriends", _addFriendsNameKey,
                                    @"Root.user", _userNameKey,
                                    @"Root.todo", _todoNameKey,
                                    @"Root.settings", _settingsNameKey,
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:
                        _inboxNameKey,
                        _iWantToNameKey,
                        _newsNameKey,
                        _todoNameKey,
                        _addFriendsNameKey,
                        _userNameKey,
                        _settingsNameKey,
                        nil] retain];
        _controllerStore = [navigators retain];
        
    }
    else {
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", _inboxNameKey,
                                    @"Root.iWantTo", _iWantToNameKey,
                                    @"Root.debug", _debugNameKey,
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:_inboxNameKey, _iWantToNameKey, _debugNameKey, nil] retain];
        _controllerStore = [navigators retain];
    }
    [self.tableView reloadData];
    if (selection) {
        NSInteger rows = [self tableView:self.tableView numberOfRowsInSection:0];
        if (selection && selection.row < rows) {
            [self.tableView selectRowAtIndexPath:selection animated:NO scrollPosition:UITableViewScrollPositionNone];
        }
    }
}



@end
