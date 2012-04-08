//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STStampsView.h"

@interface STInboxViewController ()

@end

@implementation STInboxViewController

- (id)init
{
  self = [super init];
  if (self) {
    //pass
  }
  return self;
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  STStampsView* view = [[[STStampsView alloc] initWithFrame:CGRectMake(0, 0, 320, 363)] autorelease];
  //view.backgroundColor = [UIColor redColor];
  STGenericCollectionSlice* slice = [[STGenericCollectionSlice alloc] init];
  slice.offset = [NSNumber numberWithInt:0];
  slice.limit = [NSNumber numberWithInt:NSIntegerMax];
  view.slice = slice;
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:view];
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
