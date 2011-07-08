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

static const CGFloat kFilterRowHeight = 46.0;
static const CGFloat kNormalRowHeight = 83.0;

@interface StampsListViewController ()
- (UITableViewCell*)filterCellForTableView:(UITableView*)tableView;
- (UITableViewCell*)cellForTableView:(UITableView*)tableView withEntity:(StampEntity*)entity;

@property (nonatomic, retain) NSMutableArray* stampsArray;
@end

@implementation StampsListViewController

@synthesize filterCell = filterCell_;
@synthesize stampsArray = stampsArray_;

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)dealloc {
  self.filterCell = nil;
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
    const NSString* typeStr = (NSString*)[entityLine objectAtIndex:1];
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
    NSString* userName = (NSString*)[entityLine objectAtIndex:0];
    NSString* userImg = [userName stringByReplacingOccurrencesOfString:@"." withString:@""];
    userImg = [[[[userImg lowercaseString] componentsSeparatedByString:@" "]
        componentsJoinedByString:@"_"] stringByAppendingString:@"_user_image"];
    entity.userImage = [UIImage imageNamed:userImg];
    entity.userName = userName;
    if ([entityLine count] > 3) {
      entity.comment = [(NSString*)[entityLine objectAtIndex:3]
          stringByReplacingOccurrencesOfString:@"\"" withString:@""];
    }
    entity.stampImage = [UIImage imageNamed:@"stamp_purple"];
    [stampsArray_ addObject:entity];
    [entity release];
  }

  
}

- (void)viewDidUnload {
  [super viewDidUnload];
  
  self.filterCell = nil;
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
  // Return the number of rows in the section (in addition to the filter cell).
  return [stampsArray_ count] + 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.row == 0)
    return [self filterCellForTableView:tableView];

  return [self cellForTableView:tableView withEntity:[stampsArray_ objectAtIndex:(indexPath.row - 1)]];
}

- (UITableViewCell*)filterCellForTableView:(UITableView*)tableView {
  static NSString* FilterCellIdentifier = @"FilterStampsCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:FilterCellIdentifier];

  if (cell == nil) {
    [[NSBundle mainBundle] loadNibNamed:@"StampListFilterCell" owner:self options:nil];
    cell = filterCell_;
    self.filterCell = nil;
  }

  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  gradientLayer.colors = [NSArray arrayWithObjects:
                          (id)[UIColor colorWithWhite:0.95 alpha:1.0].CGColor,
                          (id)[UIColor colorWithWhite:0.889 alpha:1.0].CGColor, nil];
  CGRect gradientFrame = cell.contentView.frame;
  //gradientFrame.size.height += 1.0;  // Account for bottom border.
  gradientLayer.frame = gradientFrame;
  // Gotta make sure the gradient is under the buttons.
  [cell.contentView.layer insertSublayer:gradientLayer atIndex:0];
  [gradientLayer release];
  
  return cell;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView withEntity:(StampEntity*)entity {
  static NSString* CellIdentifier = @"StampCell";
  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  
  if (cell == nil) {
    cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
                                   reuseIdentifier:CellIdentifier] autorelease];
  }

  // This is hacky. Fix.
  cell.contentView.layer.sublayers = nil;

  cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
  
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
  nameLabel.backgroundColor = [UIColor clearColor];
  [cell.contentView addSubview:nameLabel];
  [nameLabel release];

  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)[UIImage imageNamed:@"map_pin_small"].CGImage;
  typeIconLayer.frame = CGRectMake(leftPadding, 58, 12, 12);
  [cell.contentView.layer addSublayer:typeIconLayer];

  NSString* shortNameStr = entity.userName;
  fontString = @"Helvetica-Bold";
  stringSize = [shortNameStr sizeWithFont:[UIFont fontWithName:fontString size:12]
                                 forWidth:218
                            lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* subTextLabel = [[UILabel alloc] initWithFrame:CGRectMake(
      leftPadding + 14, 58, stringSize.width, stringSize.height)];
  subTextLabel.font = [UIFont fontWithName:fontString size:12];
  subTextLabel.textColor = [UIColor grayColor];
  subTextLabel.text = shortNameStr;
  [cell.contentView addSubview:subTextLabel];
  [subTextLabel release];
  
  if (entity.comment) {
    fontString = @"Helvetica";
    stringSize = [entity.comment sizeWithFont:[UIFont fontWithName:fontString size:12]
                                     forWidth:218 - stringSize.width - 14
                                lineBreakMode:UILineBreakModeTailTruncation];
    UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(subTextLabel.frame) + 3, 58, stringSize.width, stringSize.height)];
    commentLabel.text = entity.comment;
    commentLabel.font = [UIFont fontWithName:fontString size:12];
    commentLabel.textColor = [UIColor grayColor];
    [cell.contentView addSubview:commentLabel];
    [commentLabel release];
  }

  // Cleanup.
  [userImgLayer release];
  [typeIconLayer release];

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
