//
//  FontsViewController.m
//  FontTest
//
//  Created by Kevin Palms on 7/5/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "FontsViewController.h"


@implementation FontsViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
      
      NSLog(@"%@", [UIFont familyNames]);
      NSLog(@"%@", [UIFont fontNamesForFamilyName:@"TitlingGothicFB Comp"]);
    }
    return self;
}

- (void)dealloc
{
    [super dealloc];
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView
{
}
*/


// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
  [super viewDidLoad];
  
  // Titling Gothic Reg
  UILabel *fontA = [[UILabel alloc] initWithFrame:CGRectMake(13, 45 * 0 + 11, 300, 45)];
  fontA.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36];
  fontA.text = @"TitlingGothicFBComp-Regular";
  NSLog(@"fontA: %@", [fontA.font fontName]);
  [self.view addSubview:fontA];
  [fontA release];
  
  // TGLight (Custom metadata)
  UILabel *fontB = [[UILabel alloc] initWithFrame:CGRectMake(13, 45 * 1 + 11, 300, 45)];
  fontB.font = [UIFont fontWithName:@"TGLight" size:36];
  fontB.text = @"TGLight";
  NSLog(@"fontB: %@", [fontB.font fontName]);
  [self.view addSubview:fontB];
  [fontB release];
  
  // Titling Gothic Light
  UILabel *fontC = [[UILabel alloc] initWithFrame:CGRectMake(13, 45 * 2 + 11, 300, 45)];
  fontC.font = [UIFont fontWithName:@"TitlingGothicFBComp-Light" size:36];
  fontC.text = @"TitlingGothicFBComp-Light";
  NSLog(@"fontC: %@", [fontC.font fontName]);
  [self.view addSubview:fontC];
  [fontC release];

}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
