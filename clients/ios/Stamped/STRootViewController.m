//
//  STRootViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRootViewController.h"
#import "Util.h"
#import "STNavigationBar.h"
#import <QuartzCore/QuartzCore.h>
#import "STAppDelegate.h"
#import "STNavigationItem.h"
//
//static NSString* const kLocalDataBaseURL = @"http://localhost:18000/v0";
//#if defined (DEV_BUILD)
//static NSString* const kDataBaseURL = @"https://dev.stamped.com/v0";
//#else
//static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
//#endif
//static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";

@interface STRootViewController () <UINavigationControllerDelegate>

@property (nonatomic, readwrite, retain) UIViewController* lastController;

@end

@implementation STRootViewController

@synthesize lastController = _lastController;

- (void)dealloc
{
    [_lastController release];
    [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];

    self.delegate = (id<UINavigationControllerDelegate>)self;
    self.view.backgroundColor = [UIColor colorWithWhite:1 alpha:1];
    
    if (![self.navigationBar isKindOfClass:[STNavigationBar class]]) {
        
        STNavigationBar *bar = [[STNavigationBar alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
        bar.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self setValue:bar forKey:@"navigationBar"];
        [bar release];
        
        UITapGestureRecognizer *gridRecognizer = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(toggleGrid:)];
        gridRecognizer.numberOfTapsRequired = 3;
        gridRecognizer.numberOfTouchesRequired = 2;
        [bar addGestureRecognizer:gridRecognizer];
        [gridRecognizer release];
        
    }
    
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
    [super viewDidDisappear:animated];
}

- (void)didReceiveMemoryWarning {
}

- (void)toggleGrid:(id)nothing {
    STAppDelegate* app = (STAppDelegate*) [UIApplication sharedApplication].delegate;
    app.grid.hidden = !app.grid.hidden;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - UINavigationControllerDelegate

- (void)navigationController:(UINavigationController *)navigationController willShowViewController:(UIViewController *)viewController animated:(BOOL)animated {
    NSInteger index = [self.viewControllers indexOfObject:viewController];
    if (index!=NSNotFound && index > 0 && viewController.navigationItem.leftBarButtonItem == nil) {
        
        if (!viewController.navigationItem.hidesBackButton) {
            //UIViewController *prevController = [self.viewControllers objectAtIndex:index-1];
            STNavigationItem *button = [[STNavigationItem alloc] initWithBackButtonTitle:nil style:UIBarButtonItemStyleBordered target:self action:@selector(pop:)];
            viewController.navigationItem.leftBarButtonItem = button;
            [button release];
        }
    }
    [self.navigationBar setNeedsDisplay];
    if ([[UIDevice currentDevice].systemVersion doubleValue] < 5.0) {
        [self.lastController viewWillDisappear:animated];
        [viewController viewWillAppear:animated];
    }
}         

- (void)navigationController:(UINavigationController *)navigationController didShowViewController:(UIViewController *)viewController animated:(BOOL)animated {
    if ([[UIDevice currentDevice].systemVersion doubleValue] < 5.0) {
        [self.lastController viewDidDisappear:animated];
        [viewController viewDidAppear:animated];
        self.lastController = nil;
    }
}

- (UIViewController *)popViewControllerAnimated:(BOOL)animated {
    if ([[UIDevice currentDevice].systemVersion doubleValue] < 5.0) {
        self.lastController = self.topViewController;
    }
    return [super popViewControllerAnimated:animated];
}

- (void)pushViewController:(UIViewController *)viewController animated:(BOOL)animated {
    if ([[UIDevice currentDevice].systemVersion doubleValue] < 5.0) {
        self.lastController = self.topViewController;
    }
    return [super pushViewController:viewController animated:animated];
}

- (void)pop:(id)sender {
    
    [self popViewControllerAnimated:YES];
    
}

@end
