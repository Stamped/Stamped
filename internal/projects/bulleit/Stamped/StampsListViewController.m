//
//  StampsListViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampsListViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "StampedAppDelegate.h"
#import "StampDetailViewController.h"
#import "StampEntity.h"
#import "StampsListTableViewCell.h"
#import "UserImageView.h"

static const CGFloat kFilterRowHeight = 44.0;

typedef enum {
  StampsListFilterTypeBook,
  StampsListFilterTypeFilm,
  StampsListFilterTypeMusic,
  StampsListFilterTypePlace,
  StampsListFilterTypeOther,
  StampsListFilterTypeAll
} StampsListFilterType;

@interface StampsListViewController ()
- (void)loadTableData;
- (UITableViewCell*)cellForTableView:(UITableView*)tableView withEntity:(StampEntity*)entity;

@property (nonatomic, copy) NSArray* filterButtons;
@property (nonatomic, retain) NSMutableArray* stampsArray;
@property (nonatomic, assign) UIView* filterView;
@property (nonatomic, retain) UIButton* placesFilterButton;
@property (nonatomic, retain) UIButton* booksFilterButton;
@property (nonatomic, retain) UIButton* filmsFilterButton;
@property (nonatomic, retain) UIButton* musicFilterButton;
@end

@implementation StampsListViewController

@synthesize filterButtons = filterButtons_;
@synthesize filterView = filterView_;
@synthesize stampsArray = stampsArray_;
@synthesize placesFilterButton = placesFilterButton_;
@synthesize booksFilterButton = booksFilterButton_;
@synthesize filmsFilterButton = filmsFilterButton_;
@synthesize musicFilterButton = musicFilterButton_;

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)dealloc {
  self.filterButtons = nil;
  self.filterView = nil;
  self.stampsArray = nil;
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
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

  self.filterButtons =
      [NSArray arrayWithObjects:(id)placesFilterButton_,
                                (id)booksFilterButton_,
                                (id)filmsFilterButton_,
                                (id)musicFilterButton_, nil];
  
  self.tableView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
  // Setup filter view's gradient.
  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  gradientLayer.colors = [NSArray arrayWithObjects:
                          (id)[UIColor colorWithWhite:0.95 alpha:1.0].CGColor,
                          (id)[UIColor colorWithWhite:0.889 alpha:1.0].CGColor, nil];
  gradientLayer.frame = self.filterView.frame;
  // Gotta make sure the gradient is under the buttons.
  [self.filterView.layer insertSublayer:gradientLayer atIndex:0];
  [gradientLayer release];
  [self loadTableData];
}

- (void)viewDidUnload {
  [super viewDidUnload];

  self.filterView = nil;
  self.filterButtons = nil;
  self.stampsArray = nil;
  self.placesFilterButton = nil;
  self.booksFilterButton = nil;
  self.filmsFilterButton = nil;
  self.musicFilterButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (!userDidScroll_)
    self.tableView.contentOffset = CGPointMake(0, kFilterRowHeight);
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

- (void)loadTableData {
  // Load dummy data.
  NSString* data = [NSString stringWithContentsOfFile:
      [[NSBundle mainBundle] pathForResource:@"stamp_data" ofType:@"csv"]
                                    encoding:NSStringEncodingConversionAllowLossy
                                       error:NULL];
  NSArray* lineArray = [data componentsSeparatedByString:@"\n"];
  self.stampsArray = [NSMutableArray arrayWithCapacity:[lineArray count]];
  BOOL shouldFilter = NO;
  StampsListFilterType filterType = StampsListFilterTypeAll;
  for (UIButton* button in self.filterButtons) {
    if (button.selected) {
      shouldFilter = YES;
      if (button == placesFilterButton_) {
        filterType = StampsListFilterTypePlace;
      } else if (button == booksFilterButton_) {
        filterType = StampsListFilterTypeBook;
      } else if (button == filmsFilterButton_) {
        filterType = StampsListFilterTypeFilm;
      } else if (button == musicFilterButton_) {
        filterType = StampsListFilterTypeMusic;
      }
    }
  }
  for (NSString* line in lineArray) {
    NSArray* entityLine = [line componentsSeparatedByString:@","];
    StampEntity* entity = [[[StampEntity alloc] init] autorelease];
    entity.name = (NSString*)[entityLine objectAtIndex:2];
    NSString* typeStr = (NSString*)[entityLine objectAtIndex:1];
    entity.categoryImage = 
       [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[typeStr lowercaseString]]];
    if (!entity.categoryImage)
      entity.categoryImage = [UIImage imageNamed:@"cat_icon_other"];
  
    if ([typeStr isEqualToString:@"Place"]) {
      if (shouldFilter && filterType != StampsListFilterTypePlace)
        continue;
      entity.type = StampEntityTypePlace;
    } else if ([typeStr isEqualToString:@"Music"]) {
      if (shouldFilter && filterType != StampsListFilterTypeMusic)
        continue;
      entity.type = StampEntityTypeMusic;
    } else if ([typeStr isEqualToString:@"Film"]) {
      if (shouldFilter && filterType != StampsListFilterTypeFilm)
        continue;
      entity.type = StampEntityTypeFilm;
    } else if ([typeStr isEqualToString:@"Book"]) {
      if (shouldFilter && filterType != StampsListFilterTypeBook)
        continue;
      entity.type = StampEntityTypeBook;
    } else {
      if (shouldFilter)
        continue;
      entity.type = StampEntityTypeOther;
    }
    entity.detail = typeStr;
    NSString* userName = (NSString*)[entityLine objectAtIndex:0];
    NSString* userFile = [userName stringByReplacingOccurrencesOfString:@"." withString:@""];
    userFile = [[[userFile lowercaseString] componentsSeparatedByString:@" "]
                componentsJoinedByString:@"_"];
    entity.userImage = [UIImage imageNamed:[userFile stringByAppendingString:@"_user_image"]];
    entity.stampImage = [UIImage imageNamed:[userFile stringByAppendingString:@"_stamp_color"]];
    entity.userName = userName;
    if ([entityLine count] > 3) {
      entity.comment = [(NSString*)[entityLine objectAtIndex:3]
                        stringByReplacingOccurrencesOfString:@"\"" withString:@""];
    }

    [stampsArray_ addObject:entity];
  }
}

#pragma mark - Filter stuff

- (IBAction)filterButtonPushed:(id)sender {
  UIButton* selectedButton = (UIButton*)sender;
  for (UIButton* button in self.filterButtons)
    button.selected = (button == selectedButton && !button.selected);

  [self loadTableData];
  [self.tableView reloadData];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return [stampsArray_ count];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  return [self cellForTableView:tableView withEntity:[stampsArray_ objectAtIndex:indexPath.row]];
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView withEntity:(StampEntity*)entity {
  static NSString* CellIdentifier = @"StampCell";
  StampsListTableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[StampsListTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }

  cell.stampEntity = entity;

  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView willDisplayCell:(UITableViewCell*)cell forRowAtIndexPath:(NSIndexPath*)indexPath {
  cell.backgroundColor = [UIColor whiteColor];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  [tableView deselectRowAtIndexPath:indexPath animated:YES];
  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithEntity:[stampsArray_ objectAtIndex:indexPath.row]];

  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = [[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  userDidScroll_ = YES;
}

@end
