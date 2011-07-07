//
//  StampsListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampsListViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"

static const CGFloat kFilterRowHeight = 46.0;
static const CGFloat kNormalRowHeight = 83.0;

@implementation StampsListViewController

@synthesize stampCell = stampCell_;

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)dealloc {
  self.stampCell = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];

  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  NSLog(@"Fonts: %@", [UIFont familyNames]);
  NSLog(@"Font names: %@\n%@", [UIFont fontNamesForFamilyName:@"TGLight"],
        [UIFont fontNamesForFamilyName:@"TitlingGothicFB Comp"]);
}

- (void)viewDidUnload {
  [super viewDidUnload];
  
  self.stampCell = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (!userDidScroll_)
    self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 300;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0) {
    static NSString* FilterCellIdentifier = @"FilterStampsCell";
    UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:FilterCellIdentifier];

    if (cell == nil) {
      cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
          reuseIdentifier:FilterCellIdentifier] autorelease];
    }
    cell.selectionStyle = UITableViewCellSelectionStyleNone;
    cell.contentView.layer.backgroundColor = [UIColor lightGrayColor].CGColor;
    return cell;
  }

  static NSString* CellIdentifier = @"StampCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];

  if (cell == nil) {
    [[NSBundle mainBundle] loadNibNamed:@"StampCell" owner:self options:nil];
    cell = stampCell_;
    self.stampCell = nil;
  }

  cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
  UILabel* stampLabel = (UILabel*)[cell viewWithTag:1];
  stampLabel.text = @"Ramen Takumi";
  stampLabel.font = [UIFont fontWithName:@"TGLight" size:47];
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0)
    return;

  [tableView deselectRowAtIndexPath:indexPath animated:YES];
  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithNibName:@"StampDetailViewController" bundle:nil];

  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = [[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0)
    return kFilterRowHeight;

  return kNormalRowHeight;
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  userDidScroll_ = YES;
}

@end
