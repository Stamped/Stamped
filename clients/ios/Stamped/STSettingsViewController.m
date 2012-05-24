//
//  STSettingsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 5/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSettingsViewController.h"

@interface STSettingsViewControllerCell : NSObject

@end

@implementation <#class#>

<#methods#>

@end

@interface STSettingsViewController ()

- (void)addHeader:(NSString*)header;
- (void)addSectionWithCells:(NSArray*)cells;

@end

@implementation STSettingsViewController

- (id)init
{
    self = [super init];
    if (self) {
        // Custom initialization
    }
    return self;
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
