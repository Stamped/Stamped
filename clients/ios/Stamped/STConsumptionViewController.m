//
//  STMusicViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionViewController.h"
#import "STToolbarView.h"
#import "STGenericTableDelegate.h"
#import "STConsumptionLazyList.h"
#import "STFriendsSlice.h"
#import "STStampCellFactory.h"
#import "STCellStyles.h"

@interface STConsumptionViewController ()

@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;
@property (nonatomic, readonly, retain) STConsumptionLazyList* lazyList;

@end

@implementation STConsumptionViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize lazyList = lazyList_;

- (id)initWithCategory:(NSString*)category
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    // Custom initialization
    tableDelegate_ = [[STGenericTableDelegate alloc] init];
    lazyList_ = [[STConsumptionLazyList alloc] init];
    STFriendsSlice* slice = [[[STFriendsSlice alloc] init] autorelease];
    slice.category = category;
    slice.distance = [NSNumber numberWithInteger:1];
    slice.inclusive = [NSNumber numberWithBool:YES];
    lazyList_.genericSlice = slice;
    tableDelegate_.style = STCellStyleConsumption;
    tableDelegate_.lazyList = lazyList_;
    tableDelegate_.tableViewCellFactory = [STStampCellFactory sharedInstance];
    __block STConsumptionViewController* weak = self;
    tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
      [weak.tableView reloadData];
    };
  }
  return self;
}

- (void)dealloc
{
  [tableDelegate_ release];
  [lazyList_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self.tableDelegate;
  self.tableView.dataSource = self.tableDelegate;
	// Do any additional setup after loading the view.
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  // Release any retained subviews of the main view.
}

- (UIView *)loadToolbar {
  STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
  
  return toolbar;
}

@end
