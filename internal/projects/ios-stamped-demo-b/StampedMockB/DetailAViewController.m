//
//  DetailAViewController.m
//  StampedMockB
//
//  Created by Kevin Palms on 6/29/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "DetailAViewController.h"
#import "Stamp.h"


@interface DetailAViewController()
@property (retain) NSManagedObjectContext *managedObjectContext;
@end

@implementation DetailAViewController

@synthesize managedObjectContext, stampID;

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context
{
  self = [super init];
  if (self) {
    self.managedObjectContext = context;
  }
  
  
  return self;
}

- (UIButton *)buildEntityButtonForStamp:(Stamp *)stamp
{
  
  UIButton *entityButton = [[UIButton alloc] initWithFrame:CGRectMake(0, 0, [[UIScreen mainScreen] applicationFrame].size.width, 65)];
  //[entityButton setBackgroundColor:[UIColor lightGrayColor]];
  
  // STAMP
  UIImageView *entityStamp = [[UIImageView alloc] initWithImage:[UIImage imageNamed:[NSString stringWithFormat:@"user-stamp-%@-large.png", stamp.stampImage]]];
  CGSize expectedLabelSize = [stamp.title sizeWithFont:[UIFont fontWithName:@"TitlingGothicFB Comp" size:36] 
                                        constrainedToSize:CGSizeMake([[UIScreen mainScreen] applicationFrame].size.width - 45, 45)  
                                            lineBreakMode:UILineBreakModeTailTruncation];
  entityStamp.frame = CGRectMake((expectedLabelSize.width - 5), 0, 47, 36);
  [entityButton addSubview:entityStamp];
  [entityStamp release];
  

  // TITLE
  UILabel *entityTitle = [[UILabel alloc] initWithFrame:CGRectMake(13, 11, [[UIScreen mainScreen] applicationFrame].size.width - 45, 45)];
  [entityTitle setTextColor:[UIColor colorWithRed:0 green:0 blue:0 alpha:0.65882]];
  [entityTitle setHighlightedTextColor:[UIColor whiteColor]];
  [entityTitle setBackgroundColor:[UIColor clearColor]];
  entityTitle.font = [UIFont fontWithName:@"TitlingGothicFB Comp" size:36];
  entityTitle.numberOfLines = 1;
  entityTitle.text = stamp.title;
  [entityButton addSubview:entityTitle];
  [entityTitle release];
  
  // SUBTITLE
  UILabel *entitySubtitle = [[UILabel alloc] initWithFrame:CGRectMake(26, 47, [[UIScreen mainScreen] applicationFrame].size.width - 56, 12)];
  [entitySubtitle setTextColor:[UIColor colorWithRed:0 green:0 blue:0 alpha:0.4]];
  entitySubtitle.font = [UIFont systemFontOfSize:11];
  entitySubtitle.numberOfLines = 1;
  entitySubtitle.text = stamp.subTitle;
  [entityButton addSubview:entitySubtitle];
  [entitySubtitle release];

  // CATEGORY
  UIImageView *entityCategory = [[UIImageView alloc] initWithImage:[UIImage imageNamed:[NSString stringWithFormat:@"category-%@.png", stamp.category]]];
  entityCategory.frame = CGRectMake(14, 48, 9, 9);
  [entityButton addSubview:entityCategory];
  [entityCategory release];
  
  // ARROW
  UIImageView *entityArrow = [[UIImageView alloc] initWithFrame:CGRectMake([[UIScreen mainScreen] applicationFrame].size.width - 22, 26, 8, 12)];
  entityArrow.image = [UIImage imageNamed:@"cell-arrow.png"];
  [entityButton addSubview:entityArrow];
  [entityArrow release];
  
  
  return entityButton;
}

- (void)viewDidLoad {
  Stamp *stamp = (Stamp *)[self.managedObjectContext objectWithID:self.stampID];
  NSLog(@"Got data for: %@", stamp);
  
  
  UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0, 0, [[UIScreen mainScreen] applicationFrame].size.width, [[UIScreen mainScreen] applicationFrame].size.height)];
  [self.view setBackgroundColor:[UIColor colorWithPatternImage:[UIImage imageNamed:@"detail-bg.png"]]];
  
  self.view = view;
  
  UIButton *entityButton = [self buildEntityButtonForStamp:stamp];
  [self.view addSubview:entityButton];
  [entityButton release];
  
  UIView *contentView = [[UIView alloc] initWithFrame:CGRectMake(5, 69, [[UIScreen mainScreen] applicationFrame].size.width - 10, 400)];
  
  UIView *topBorderColor = [[UIView alloc] initWithFrame:CGRectMake(0, 0, contentView.frame.size.width, 4)];
  UIColor *color = (stamp.color) ? stamp.color : [UIColor redColor];
  [topBorderColor setBackgroundColor:color];
  UIView *topBorder = [[UIView alloc] initWithFrame:topBorderColor.frame];
  [topBorder setBackgroundColor:[UIColor colorWithPatternImage:[UIImage imageNamed:@"detail-border-top.png"]]];
  [topBorder setOpaque:NO];
  
  [contentView addSubview:topBorderColor];
  [contentView addSubview:topBorder];
  [topBorderColor release];
  [topBorder release];
  
  // STAMP DETAILS
  UIImageView *avatar = [[UIImageView alloc] initWithFrame:CGRectMake(10, 12, 54, 54)];
  avatar.image = [UIImage imageNamed:[NSString stringWithFormat:@"user-image-%@-large.png", stamp.avatar]];
  [contentView addSubview:avatar];
  [avatar release];
  
  UILabel *userName = [[UILabel alloc] initWithFrame:CGRectMake(75, 18, contentView.frame.size.width - 90, 14)];
  userName.text = [NSString stringWithFormat:@"%@ stamped", stamp.userName];
  [userName setTextColor:[UIColor colorWithRed:0 green:0 blue:0 alpha:0.3]];
  userName.font = [UIFont boldSystemFontOfSize:13];
  [contentView addSubview:userName];
  [userName release];
  
  UILabel *stampText = [[UILabel alloc] initWithFrame:CGRectMake(75, 35, contentView.frame.size.width - 90, 14)];
  stampText.font = [UIFont systemFontOfSize:13];
  stampText.text = stamp.comment;
  [stampText setTextColor:[UIColor colorWithRed:0 green:0 blue:0 alpha:.8]];
  stampText.numberOfLines = 0;
  stampText.lineBreakMode = UILineBreakModeWordWrap;
  
	CGSize maximumLabelSize = CGSizeMake(stampText.frame.size.width,9999);
	CGSize expectedLabelSize = [stampText.text sizeWithFont:stampText.font 
                                        constrainedToSize:maximumLabelSize 
                                            lineBreakMode:UILineBreakModeWordWrap]; 
	CGRect newFrame = stampText.frame;
	newFrame.size.height = expectedLabelSize.height;
	stampText.frame = newFrame;
  
  [contentView addSubview:stampText];
  
  int imageHeight = avatar.frame.origin.y + avatar.frame.size.height;
  int commentHeight = stampText.frame.origin.y + stampText.frame.size.height;
  int contentHeight = (imageHeight > commentHeight) ? imageHeight : commentHeight;
  
  contentView.frame = CGRectMake(contentView.frame.origin.x, contentView.frame.origin.y, contentView.frame.size.width, contentHeight + 12);
  [stampText release];
  
  [contentView setBackgroundColor:[UIColor whiteColor]];
  
  
  
  UIView *bottomBorderColor = [[UIView alloc] initWithFrame:CGRectMake(0, contentView.frame.size.height - 4, contentView.frame.size.width, 4)];
  [bottomBorderColor setBackgroundColor:color];
  UIView *bottomBorder = [[UIView alloc] initWithFrame:bottomBorderColor.frame];
  [bottomBorder setBackgroundColor:[UIColor colorWithPatternImage:[UIImage imageNamed:@"detail-border-bottom.png"]]];
  [bottomBorder setOpaque:NO];
  
  [contentView addSubview:bottomBorderColor];
  [contentView addSubview:bottomBorder];
  [bottomBorderColor release];
  [bottomBorder release];
  
  
  [self.view addSubview:contentView];
  [contentView release];
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

/*
// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
    [super viewDidLoad];
}
*/

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
