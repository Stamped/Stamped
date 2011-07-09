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

static const CGFloat kFilterRowHeight = 44.0;

@interface StampsListViewController ()
- (UITableViewCell*)cellForTableView:(UITableView*)tableView withEntity:(StampEntity*)entity;

@property (nonatomic, retain) NSMutableArray* stampsArray;
@end

@implementation StampsListViewController

@synthesize filterView = filterView_;
@synthesize stampsArray = stampsArray_;

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)dealloc {
  self.filterView = nil;
  self.stampsArray = nil;
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

  // Load dummy data.
  NSString* data = [NSString stringWithContentsOfFile:
      [[NSBundle mainBundle] pathForResource:@"stamp_data" ofType:@"csv"]
      encoding:NSStringEncodingConversionAllowLossy error:NULL];
  NSArray* lineArray = [data componentsSeparatedByString:@"\n"];
  self.stampsArray = [NSMutableArray arrayWithCapacity:[lineArray count]];
  for (NSString* line in lineArray) {
    NSArray* entityLine = [line componentsSeparatedByString:@","];
    //NSLog(@"%@", entityLine);
    StampEntity* entity = [[StampEntity alloc] init];
    entity.name = (NSString*)[entityLine objectAtIndex:2];
    NSString* typeStr = (NSString*)[entityLine objectAtIndex:1];
    entity.categoryImage = 
        [UIImage imageNamed:[@"cat_icon_" stringByAppendingString:[typeStr lowercaseString]]];
    if (!entity.categoryImage)
      entity.categoryImage = [UIImage imageNamed:@"cat_icon_place"];

    if (typeStr == @"Place") {
      entity.type = StampEntityTypePlace;
    } else if (typeStr == @"Music") {
      entity.type = StampEntityTypeMusic;
    } else if (typeStr == @"Film") {
      entity.type = StampEntityTypeFilm;
    } else if (typeStr == @"Book") {
      entity.type = StampEntityTypeBook;
    } else {
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
    [entity release];
  }

  
}

- (void)viewDidUnload {
  [super viewDidUnload];
  
  self.filterView = nil;
  self.stampsArray = nil;
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

#pragma mark - Filter stuff

- (IBAction)filterButtonPushed:(id)sender {
  UIButton* button = (UIButton*)sender;
  [button setSelected:!button.selected];
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
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                   reuseIdentifier:CellIdentifier] autorelease];
    cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
  }

  // TODO(andybons): Use layer caching for this shit.
  cell.contentView.layer.sublayers = nil;

  CALayer* userImgLayer = [[CALayer alloc] init];
  userImgLayer.contents = (id)entity.userImage.CGImage;
  userImgLayer.contentsGravity = kCAGravityResizeAspect;
  userImgLayer.frame = CGRectMake(14, 8, 37, 37);
  userImgLayer.borderColor = [UIColor whiteColor].CGColor;
  userImgLayer.borderWidth = 2.0;
  userImgLayer.shadowOpacity = 0.5;
  userImgLayer.shadowOffset = CGSizeMake(0, 0.5);
  userImgLayer.shadowRadius = 1.0;
  userImgLayer.shadowPath = [UIBezierPath bezierPathWithRect:userImgLayer.bounds].CGPath;
  [cell.contentView.layer addSublayer:userImgLayer];

  const CGFloat leftPadding = CGRectGetMaxX(userImgLayer.frame) + 14;
  NSString* fontString = @"TGLight";
  CGSize stringSize = [entity.name sizeWithFont:[UIFont fontWithName:fontString size:47]
                                       forWidth:225
                                  lineBreakMode:UILineBreakModeTailTruncation];
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(leftPadding + stringSize.width - (23 / 2), 7, 23, 23);
  stampLayer.contents = (id)entity.stampImage.CGImage;
  [cell.contentView.layer addSublayer:stampLayer];
  [stampLayer release];
  
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(
      leftPadding, 8, stringSize.width, stringSize.height)];
  nameLabel.font = [UIFont fontWithName:fontString size:47];
  nameLabel.text = entity.name;
  nameLabel.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  nameLabel.backgroundColor = [UIColor clearColor];
  [cell.contentView addSubview:nameLabel];
  [nameLabel release];

  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)entity.categoryImage.CGImage;
  typeIconLayer.frame = CGRectMake(leftPadding, 59, 12, 12);
  [cell.contentView.layer addSublayer:typeIconLayer];

  fontString = @"Helvetica-Bold";
  stringSize = [entity.userName sizeWithFont:[UIFont fontWithName:fontString size:12]
                                    forWidth:218
                               lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* subTextLabel = [[UILabel alloc] initWithFrame:CGRectMake(
      leftPadding + 16, 58, stringSize.width, stringSize.height)];
  subTextLabel.font = [UIFont fontWithName:fontString size:12];
  subTextLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  subTextLabel.text = entity.userName;
  [cell.contentView addSubview:subTextLabel];
  [subTextLabel release];
  
  if (entity.comment) {
    fontString = @"HelveticaNeue";
    stringSize = [entity.comment sizeWithFont:[UIFont fontWithName:fontString size:12]
                                     forWidth:218 - stringSize.width - 14
                                lineBreakMode:UILineBreakModeTailTruncation];
    UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(subTextLabel.frame) + 3, 58, stringSize.width, stringSize.height)];
    commentLabel.text = entity.comment;
    commentLabel.font = [UIFont fontWithName:fontString size:12];
    commentLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    [cell.contentView addSubview:commentLabel];
    [commentLabel release];
  }

  // Cleanup.
  [userImgLayer release];
  [typeIconLayer release];

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
