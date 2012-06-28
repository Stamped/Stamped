//
//  STLeftMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

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

#define kAvatarViewTag 101

static NSString* const _inboxNameKey = @"Root.inboxName";
static NSString* const _iWantToNameKey = @"Root.iWantToName";
static NSString* const _newsNameKey = @"Root.newsName";
static NSString* const _addFriendsNameKey = @"Root.addFriendsName";
static NSString* const _userNameKey = @"Root.userName";
static NSString* const _debugNameKey = @"Root.debugName";
static NSString* const _todoNameKey = @"Root.todoName";
static NSString* const _settingsNameKey = @"Root.settingsName";

@interface STLeftMenuViewController ()

@property (nonatomic, readonly, retain) UIView* titleView;
@property (nonatomic, readonly, retain) UIView* playerView;
@property (nonatomic, readonly, retain) UILabel* playerTitleView;

@end

@implementation STLeftMenuViewController

@synthesize tableView=_tableView;
@synthesize anchorTableView=_anchorTableView;
@synthesize titleView = _titleView;
@synthesize playerView = _playerView;
@synthesize playerTitleView = _playerTitleView;

- (id)init {
    if ((self = [super init])) {
        _selectedIndexPath = [[NSIndexPath indexPathForRow:0 inSection:0] retain];
        [self loginStatusChanged:nil];
        
    }
    return self;
}

- (void)dealloc {
    self.tableView = nil;
    [_selectedIndexPath release], _selectedIndexPath=nil;
    [_dataSource release], _dataSource=nil;;
    [_controllerStore release], _controllerStore=nil;
    [_anchorDataSource release], _anchorDataSource=nil;
    [_anchorControllerStore release], _anchorControllerStore=nil;
    [_titleView release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStylePlain];
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.rowHeight = 48.0f;
        tableView.scrollEnabled = NO;
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]];
        tableView.backgroundView = imageView;
        [imageView release];
        
        imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"left_logo.png"]] autorelease];
        UIView *view = [[[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 50.0f)] autorelease];
        [view addSubview:imageView];
        self.tableView.tableHeaderView = view;
        _titleView = imageView;
        
        _playerView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 100)];
        _playerTitleView = [[UILabel alloc] initWithFrame:CGRectMake(50, 0, 180, 50)];
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
        
    }
    
    if (!_anchorTableView) {
        
        CGRect frame = self.view.bounds;
        frame.size.height = 48.0f * [_anchorDataSource count];
        frame.origin.y = (self.view.bounds.size.height - frame.size.height);
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:frame style:UITableViewStylePlain];
        tableView.backgroundColor = [UIColor clearColor];
        tableView.scrollEnabled = NO;
        tableView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleWidth;
        tableView.rowHeight = 48.0f;
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view insertSubview:tableView aboveSubview:self.tableView];
        self.anchorTableView = tableView;
        
        UIImage *image = [UIImage imageNamed:@"left_menu_anchor_shadow.png"];
        UIImageView *shadow = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        shadow.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleWidth;
        [self.view addSubview:shadow];
        [shadow release];
        
        frame = shadow.bounds;
        frame.size.width = self.view.bounds.size.width;
        frame.origin.y = (tableView.frame.origin.y - frame.size.height);
        shadow.frame = frame;
        
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:tableView.bounds];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        view.contentMode = UIViewContentModeRedraw;
        view.alpha = 0.1f;
        view.backgroundColor = [UIColor clearColor];
        [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            drawGradient([UIColor colorWithRed:0.851f green:0.851f blue:0.851f alpha:1.0f].CGColor, [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f].CGColor, ctx);
            
        }];
        tableView.backgroundView = view;
        [view release];
        [tableView release];
        
    }
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(configurationChanged:) name:STConfigurationValueDidChangeNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(loginStatusChanged:) name:STStampedAPILoginNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(loginStatusChanged:) name:STStampedAPILogoutNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(playerStateChanged:) name:STPlayerStateChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(playerItemChanged:) name:STPlayerItemChangedNotification object:nil];
    [self playerStateChanged:nil];
}

- (void)viewDidUnload {
    self.tableView = nil;
    self.anchorTableView = nil;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super viewDidUnload];
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
    [self.anchorTableView deselectRowAtIndexPath:self.anchorTableView.indexPathForSelectedRow animated:YES];
    
    if (_selectedIndexPath) {
        [self.tableView selectRowAtIndexPath:_selectedIndexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
    }
    
}


#pragma mark - Icon Helper

- (NSString*)iconTitleForTableView:(UITableView*)tableView atIndex:(NSInteger)index {
    
    if (tableView == _tableView) {
        
        switch (index) {
            case 0:
                return @"left_menu_icon_stamps.png";
                break;
            case 1:
                return @"left_menu_icon_iwantto.png";
                break;
            case 2:
                return @"left_menu_icon_news.png";
                break;
            case 3:
                return @"left_menu_icon_friends.png";
                break;
            case 4:
                return @"left_menu_icon_stamps.png";
                break;
            default:
                break;
        }
        
    } else {
        
        switch (index) {
            case 0:
                return @"left_menu_icon_to-do.png";
                break;
            case 1:
                return @"left_menu_icon_settings.png";
                break;                
            default:
                break;
        }
        
    }
    
    return nil;
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return (tableView==self.tableView) ? [_dataSource count] : [_anchorDataSource count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView==self.tableView) {
        
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
        
        if (indexPath.row == 4 && LOGGED_IN) {
            
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
    
    static NSString *AnchorCellIdentifier = @"AnchorCellIdentifier";
    
    LeftMenuTableCell *cell = (LeftMenuTableCell*)[tableView dequeueReusableCellWithIdentifier:AnchorCellIdentifier];
    if (cell == nil) {
        cell = [[[LeftMenuTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:AnchorCellIdentifier] autorelease];
    }
    
    cell.titleLabel.textColor = [UIColor colorWithRed:0.4f green:0.4f blue:0.4f alpha:1.0f];
    [cell setTop:(indexPath.row!=0) bottom:YES];
    cell.titleLabel.text = [STConfiguration value:[_anchorDataSource objectAtIndex:indexPath.row]];
    cell.icon = [UIImage imageNamed:[self iconTitleForTableView:tableView atIndex:indexPath.row]];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    
    if (!_anchorSelected && self.tableView == tableView  && _selectedIndexPath && [_selectedIndexPath isEqual:indexPath]) {
        
        // controller is already root, lets just pop it to root like a tab bar
        STMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
        UINavigationController *navController = (UINavigationController*)[menuController rootViewController];
        if (navController && [navController isKindOfClass:[UINavigationController class]]) {
            [menuController showRootController:YES];
            [navController popToRootViewControllerAnimated:NO];
            return;
        }
        
    }
    
    
    NSString *key = (tableView == self.tableView) ? [_dataSource objectAtIndex:indexPath.row] : [_anchorDataSource objectAtIndex:indexPath.row];
    NSString *value = (tableView == self.tableView) ? [_controllerStore objectForKey:key] : [_anchorControllerStore objectForKey:key];
    
    UIViewController *controller = nil;
    
    if ([[STConfiguration value:value] isEqual:[STUserViewController class]]) {
        
        id user = [[STStampedAPI sharedInstance] currentUser];
        controller = [[STUserViewController alloc] initWithUser:(STSimpleUserDetail*)user];
        
    } else {
        
        controller = [[[STConfiguration value:value] alloc] init];
        
    }
    
    _anchorSelected = (self.anchorTableView == tableView);
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    STMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    
    if (self.tableView == tableView || YES) {
        
        [menuController setRootController:navController animated:YES];
        [Util addHomeButtonToController:controller withBadge:![controller isKindOfClass:[STUniversalNewsController class]]];
        
    } 
    else {
        
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
        controller.navigationItem.rightBarButtonItem = item;
        [item release];
        
        [menuController presentModalViewController:navController animated:YES];
        
    }
    [controller release];
    [navController release];
    
    if (tableView == self.tableView) {
        
        if (![indexPath isEqual:_selectedIndexPath]) {
            UITableViewCell *cell = [self.tableView cellForRowAtIndexPath:_selectedIndexPath];
            [cell setSelected:NO];
        }
        
        [_selectedIndexPath release], _selectedIndexPath=nil;
        _selectedIndexPath = [indexPath retain];
        
    }
    [self performSelector:@selector(loginStatusChanged:) withObject:nil afterDelay:.3];
}


#pragma mark - LeftMenuTableCellDelegate

- (void)leftMenuTableCellHighlighted:(LeftMenuTableCell*)cell {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    
    if (_selectedIndexPath) {
        if (![indexPath isEqual:_selectedIndexPath]) {
            UITableViewCell *selectedCell = [self.tableView cellForRowAtIndexPath:_selectedIndexPath];
            [selectedCell setSelected:!cell.highlighted];
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

- (void)loginStatusChanged:(id)notImportant {
    
    [_dataSource release];
    [_controllerStore release];
    [_anchorControllerStore release];
    [_anchorDataSource release];
    if (LOGGED_IN || YES) {
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", _inboxNameKey,
                                    @"Root.iWantTo", _iWantToNameKey,
                                    @"Root.news", _newsNameKey,
                                    @"Root.findFriends", _addFriendsNameKey,
                                    @"Root.user", _userNameKey,
                                    @"Root.debug", _debugNameKey,
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:_inboxNameKey, _iWantToNameKey, _newsNameKey, _addFriendsNameKey, _userNameKey, _debugNameKey, nil] retain];
        _controllerStore = [navigators retain];
        
        _anchorControllerStore = [[NSDictionary dictionaryWithObjectsAndKeys:@"Root.todo", _todoNameKey, @"Root.settings", _settingsNameKey,
                                   nil] retain];
        _anchorDataSource = [[NSArray arrayWithObjects:_todoNameKey, _settingsNameKey, nil] retain];
    }
    else {
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", _inboxNameKey,
                                    @"Root.iWantTo", _iWantToNameKey,
                                    @"Root.debug", _debugNameKey,
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:_inboxNameKey, _iWantToNameKey, _debugNameKey, nil] retain];
        _controllerStore = [navigators retain];
        
        _anchorControllerStore = [[NSDictionary dictionary] retain];
        _anchorDataSource = [[NSArray array] retain];
    }
    [self.tableView reloadData];
    [self.anchorTableView reloadData];
}



@end
