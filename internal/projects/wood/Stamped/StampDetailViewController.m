//
//  StampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

@implementation StampDetailViewController

- (id)initWithStyle:(UITableViewStyle)style {
  self = [super initWithStyle:style];
  if (self) {}
  return self;
}

- (void)dealloc {
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
}

- (void)viewDidUnload {
  [super viewDidUnload];
  // Release any retained subviews of the main view.
  // e.g. self.myOutlet = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
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
  // Return the number of sections.
  return 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  // Return the number of rows in the section.
  return 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  static NSString* CellIdentifier = @"Cell";

  UITableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault
        reuseIdentifier:CellIdentifier] autorelease];
  }
  NSString* nameString = @"Ramen Takumi Slut";
  NSString* fontString = @"TGLight";
  CGSize stringSize = [nameString sizeWithFont:[UIFont fontWithName:fontString size:47]
                                      forWidth:280
                                 lineBreakMode:UILineBreakModeTailTruncation];
  
  cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
  cell.selectionStyle = UITableViewCellSelectionStyleNone;
  CTFontRef nameFont = CTFontCreateWithName((CFStringRef)fontString, 47, NULL);
  NSDictionary* strAttributes = [NSDictionary dictionaryWithObjectsAndKeys:
      (id)nameFont, (id)kCTFontAttributeName, nil];

  NSAttributedString* nameAttributedString =
      [[NSAttributedString alloc] initWithString:nameString
                                      attributes:strAttributes];

  CATextLayer* nameLayer = [[CATextLayer alloc] init];
  nameLayer.frame = CGRectMake(10, 10, stringSize.width, stringSize.height);
  nameLayer.contentsScale = [[UIScreen mainScreen] scale];
  nameLayer.truncationMode = kCATruncationEnd;
  // Needed for the ellipsis.
  nameLayer.foregroundColor = [UIColor blackColor].CGColor;
  nameLayer.string = nameAttributedString;

  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(10 + stringSize.width - (46 / 2),
                                10 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)[UIImage imageNamed:@"stamp_purple"].CGImage;

  [cell.contentView.layer addSublayer:stampLayer];
  [cell.contentView.layer addSublayer:nameLayer];

  // Cleanup.
  CFRelease(nameFont);
  [stampLayer release];
  [nameLayer release];
  [nameAttributedString release];
  
  return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  // Navigation logic may go here. Create and push another view controller.
  /*
   <#DetailViewController#> *detailViewController = [[<#DetailViewController#> alloc] initWithNibName:@"<#Nib name#>" bundle:nil];
   // ...
   // Pass the selected object to the new view controller.
   [self.navigationController pushViewController:detailViewController animated:YES];
   [detailViewController release];
   */
}

@end
