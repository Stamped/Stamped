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

@implementation STLeftMenuViewController

@synthesize tableView= _tableView;

- (id)init {
    if ((self = [super init])) {
        
        NSDictionary *navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                    @"Root.inbox", @"Stamps",
                                    @"Root.iWantTo", @"I Want to...",
                                    @"Root.news", @"News",
                                    @"Root.todo", @"To-Do",
                                    @"Root.debug", @"Debug",
                                    @"Root.settings", @"Settings",
                                    nil];
        NSArray *navigatorOrder = [NSArray arrayWithObjects:@"Stamps", @"I Want to...", @"News", @"To-Do", @"Debug", @"Settings", nil];
        _dataSource = [navigatorOrder retain];
        _controllerStore = [navigators retain];
        
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
    self.tableView = nil;
    [_dataSource release], _dataSource=nil;;
    [_controllerStore release], _controllerStore=nil;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_tableView) {
        
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:UITableViewStylePlain];
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        self.tableView = tableView;
        [tableView release];
        
        UIImageView *backgroundImage = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]];
        tableView.backgroundView = backgroundImage;
        [backgroundImage release];

        UIView *stampedLabel = [Util viewWithText:@"STAMPED" 
                                             font:[UIFont stampedTitleFontWithSize:30] 
                                            color:[UIColor colorWithWhite:0 alpha:.5]
                                             mode:UILineBreakModeClip 
                                       andMaxSize:CGSizeMake(320, CGFLOAT_MAX)];
        stampedLabel.frame = CGRectMake(20, 0, self.view.bounds.size.width, 50);
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 80.0f)];
        [view addSubview:stampedLabel];
        self.tableView.tableHeaderView = view;
        [view release];

    }

}

- (void)viewDidUnload {
    [super viewDidUnload];
    self.tableView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [_dataSource count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    cell.textLabel.text = [_dataSource objectAtIndex:indexPath.row];
    
    return cell;
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    NSString *key = [_dataSource objectAtIndex:indexPath.row];
    UIViewController *controller = [[[STConfiguration value:[_controllerStore objectForKey:key]] alloc] init];
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    DDMenuController *menuController = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [menuController setRootController:navController animated:YES];
    [controller release];
    [navController release];

}


@end
