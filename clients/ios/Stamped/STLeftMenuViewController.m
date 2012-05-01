//
//  STLeftMenuViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLeftMenuViewController.h"
#import "STRootMenuView.h"
#import "Util.h"

@interface STLeftMenuViewController ()

@end

@implementation STLeftMenuViewController

- (id)init
{
    self = [super init];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)loadView {
  UIView* view = [[[UIView alloc] initWithFrame:[Util standardFrameWithNavigationBar:NO]] autorelease];
  UIScrollView* scroller = [[[UIScrollView alloc] initWithFrame:[Util standardFrameWithNavigationBar:NO]] autorelease];
  //scroller.backgroundColor = [UIColor colorWithWhite:.3 alpha:1];
  scroller.contentSize = CGSizeMake(scroller.frame.size.width, scroller.frame.size.height+1);
  [scroller addSubview:[STRootMenuView sharedInstance]];
  scroller.scrollsToTop = NO;
  UIImageView* backgroundImage = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"menu_background"]] autorelease];
  [view addSubview:backgroundImage];
  [view addSubview:scroller];
  self.view = view;
}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view.
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
