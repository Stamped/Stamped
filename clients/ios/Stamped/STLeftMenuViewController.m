//
//  STLeftMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLeftMenuViewController.h"
#import "Util.h"
#import "DDMenuController.h"
#import "SettingsViewController.h"
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


@implementation STLeftMenuViewController

@synthesize tableView=_tableView;
@synthesize anchorTableView=_anchorTableView;

- (id)init {
    if ((self = [super init])) {
        
        _selectedIndexPath = [[NSIndexPath indexPathForRow:0 inSection:0] retain];
        
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", @"Stamps",
                                    @"Root.iWantTo", @"I Want to...",
                                    @"Root.news", @"News",
                                    @"Root.debug", @"Debug",
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:@"Stamps", @"I Want to...", @"News", @"Debug", nil] retain];
        _controllerStore = [navigators retain];
        
        _anchorControllerStore = [[NSDictionary dictionaryWithObjectsAndKeys:@"Root.todo", @"To-Do", @"Root.settings", @"Settings",
                      nil] retain];
        _anchorDataSource = [[NSArray arrayWithObjects:@"To-Do", @"Settings", nil] retain];
        
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
    self.tableView = nil;
    [_selectedIndexPath release], _selectedIndexPath=nil;
    [_dataSource release], _dataSource=nil;;
    [_controllerStore release], _controllerStore=nil;
    [_anchorDataSource release], _anchorDataSource=nil;
    [_anchorControllerStore release], _anchorControllerStore=nil;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    [[STStampedAPI sharedInstance] unreadCountWithCallback:^(id<STActivityCount> count, NSError *error, STCancellation *cancellation) {
        if (count && count.numberUnread.integerValue > 0) {
            _unreadCount = count.numberUnread.integerValue;
            [self.tableView reloadData];
        }
    }];
    
    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStylePlain];
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.rowHeight = 48.0f;
        tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]];
        tableView.backgroundView = imageView;
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"left_logo.png"]];
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 50.0f)];
        [view addSubview:imageView];
        self.tableView.tableHeaderView = view;
        [view release];
        [imageView release];
        
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
        tableView.scrollEnabled = NO;
        tableView.backgroundColor = [UIColor clearColor];
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
        [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {

            drawGradient([UIColor colorWithRed:0.851f green:0.851f blue:0.851f alpha:1.0f].CGColor, [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f].CGColor, ctx);

        }];
        tableView.backgroundView = view;
        [view release];
        [tableView release];
        
    }
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    self.tableView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.anchorTableView deselectRowAtIndexPath:self.anchorTableView.indexPathForSelectedRow animated:YES];
    
    if (_selectedIndexPath) {
        [self.tableView selectRowAtIndexPath:_selectedIndexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
    }
    
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
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
        
        cell.titleLabel.text = [_dataSource objectAtIndex:indexPath.row];
        cell.border = YES;
        
        if ([cell.titleLabel.text isEqualToString:@"News"]) {
            [cell setBadgeCount:_unreadCount];
        } else {
            [cell setBadgeCount:0];
        }
        
        cell.icon = [UIImage imageNamed:[NSString stringWithFormat:@"left_menu_icon_%@.png", [cell.titleLabel.text lowercaseString]]];
        
        if ([indexPath isEqual:_selectedIndexPath]) {
            cell.selected = YES;
        }
        
        return cell;
        
    }
    
    static NSString *CellIdentifier = @"AnchorCellIdentifier";
    
    LeftMenuTableCell *cell = (LeftMenuTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[LeftMenuTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    cell.titleLabel.textColor = [UIColor colorWithRed:0.4f green:0.4f blue:0.4f alpha:1.0f];
    cell.topBorder = (indexPath.row==1);
    cell.titleLabel.text = [_anchorDataSource objectAtIndex:indexPath.row];
    cell.icon = [UIImage imageNamed:[NSString stringWithFormat:@"left_menu_icon_%@.png", [cell.titleLabel.text lowercaseString]]];

    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    
    if (self.tableView == tableView  && _selectedIndexPath && [_selectedIndexPath isEqual:indexPath]) {
        
        // controller is already root, lets just pop it to root like a tab bar
        DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
        UINavigationController *navController = (UINavigationController*)[menuController rootViewController];
        if (navController && [navController isKindOfClass:[UINavigationController class]]) {
            [menuController showRootController:YES];
            [navController popToRootViewControllerAnimated:NO];
            return;
        }
        
    }
    
    
    NSString *key = (tableView == self.tableView) ? [_dataSource objectAtIndex:indexPath.row] : [_anchorDataSource objectAtIndex:indexPath.row];
    NSString *value = (tableView == self.tableView) ? [_controllerStore objectForKey:key] : [_anchorControllerStore objectForKey:key];
    
    UIViewController *controller = [[[STConfiguration value:value] alloc] init];
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;

    if (self.tableView == tableView || [key isEqualToString:@"To-Do"]) {
        
        [menuController setRootController:navController animated:YES];
        
    } else {
        
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
    
    UIViewController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller dismissModalViewControllerAnimated:YES];
    
}


@end
