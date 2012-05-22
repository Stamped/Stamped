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
#import "STLegacyInboxViewController.h"
#import "SettingsViewController.h"
#import "STUniversalNewsController.h"
#import "STTodoViewController.h"
#import "STDebugViewController.h"
#import "ECSlidingViewController.h"
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
                                    @"Root.todo", @"To-Do",
                                    nil];
        _dataSource = [[NSArray arrayWithObjects:@"Stamps", @"I Want to...", @"News", @"To-Do", nil] retain];
        _controllerStore = [navigators retain];
        
        _anchorControllerStore = [[NSDictionary dictionaryWithObjectsAndKeys:
                                   @"Root.debug", @"Debug",
                                   @"Root.settings", @"Settings",
                                   nil] retain];
        _anchorDataSource = [[NSArray arrayWithObjects:@"Debug", @"Settings", nil] retain];
        
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
            //count.numberUnread.integerValue
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
        [self.view addSubview:tableView];
        self.anchorTableView = tableView;
        
        /*
         tableView.layer.shadowPath = [UIBezierPath bezierPathWithRect:tableView.bounds].CGPath;
         tableView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
         tableView.layer.shadowRadius = 16.0f;
         tableView.layer.shadowOpacity = 0.4f;
         */
        
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:tableView.bounds];
        view.contentMode = UIViewContentModeRedraw;
        view.alpha = 0.1f;
        view.backgroundColor = [UIColor clearColor];
        [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            
            //CGContextSetAlpha(ctx, 0.1);
            drawGradient([UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f].CGColor, [UIColor colorWithRed:0.851f green:0.851f blue:0.851f alpha:1.0f].CGColor, ctx);
            
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
        
        if ([indexPath isEqual:_selectedIndexPath]) {
            cell.selected = YES;
        }
        
        return cell;
        
    }
    
    static NSString *CellIdentifier = @"AnchorCellIdentifier";
    
    LeftMenuTableCell *cell = (LeftMenuTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[LeftMenuTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.selectionStyle = UITableViewCellSelectionStyleNone;
    }
    
    cell.topBorder = YES;
    cell.titleLabel.text = [_anchorDataSource objectAtIndex:indexPath.row];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    NSString* configKey = nil;
    if (tableView == self.tableView) {
        NSString* key = [_dataSource objectAtIndex:indexPath.row];
        configKey = [_controllerStore objectForKey:key];
    }
    else {
        NSString* key = [_anchorDataSource objectAtIndex:indexPath.row];
        configKey = [_anchorControllerStore objectForKey:key];
    }
    UIViewController *controller = [[[STConfiguration value:configKey] alloc] init];
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    if (self.tableView == tableView) {
        [menuController setRootController:navController animated:YES];
    } else {
        [menuController setRootController:navController animated:YES];
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


@end
