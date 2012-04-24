//
//  STDebugViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDebugViewController.h"
#import "STDebug.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STRootMenuView.h"
#import "STDebugDatumViewController.h"
#import "Util.h"
#import "ECSlidingViewController.h"

@interface STDebugCell : UITableViewCell

- (id)initWithDatum:(STDebugDatum*)datum;

@end

@implementation STDebugCell

- (id)initWithDatum:(STDebugDatum*)datum {
  self = [super initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"test"];
  if (self) {
    self.textLabel.text = [NSString stringWithFormat:@"%@", datum.object];
    self.detailTextLabel.text = [NSString stringWithFormat:@"%@", datum.created];
    self.textLabel.font = [UIFont stampedFontWithSize:12];
    self.textLabel.textColor = [UIColor stampedDarkGrayColor];
    self.detailTextLabel.font = [UIFont stampedFontWithSize:12];
    self.detailTextLabel.textColor = [UIColor stampedGrayColor];
    self.textLabel.lineBreakMode = UILineBreakModeTailTruncation;
  }
  return self;
}

@end

@interface STDebugViewController () <UITableViewDelegate, UITableViewDataSource>

@end

@implementation STDebugViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)backButtonClicked:(id)button {
  [self.slidingViewController anchorTopViewTo:ECRight];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self;
  self.tableView.dataSource = self;
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
}

- (void)viewDidAppear:(BOOL)animated {
  [self.tableView reloadData];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return [STDebug sharedInstance].logCount;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  STDebugDatum* datum = [[STDebug sharedInstance] logItemAtIndex:([STDebug sharedInstance].logCount - (indexPath.row + 1))];
  return [[[STDebugCell alloc] initWithDatum:datum] autorelease];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  STDebugDatum* datum = [[STDebug sharedInstance] logItemAtIndex:([STDebug sharedInstance].logCount - (indexPath.row + 1))];
  [[Util sharedNavigationController] pushViewController:[[[STDebugDatumViewController alloc] initWithDatum:datum] autorelease] animated:YES];
}

- (void)reloadStampedData {
  [self.tableView reloadData];
}

@end
