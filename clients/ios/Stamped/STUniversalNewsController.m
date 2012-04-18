//
//  STUniversalNewsController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUniversalNewsController.h"
#import "STRootMenuView.h"

@interface STUniversalNewsController ()

@property (nonatomic, readonly, retain) NSMutableArray* newsItems;

@end

@implementation STUniversalNewsController

- (id)init {
  self = [super initWithHeaderHeight:0];
  if (self) {
    
  }
  return self;
}

- (void)backButtonClicked:(id)button {
  [[STRootMenuView sharedInstance] toggle];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
