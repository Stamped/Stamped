    //
//  StampDetailViewController.m
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "StampDetailViewController.h"
#import "Stamp.h"
#import "User.h"

@interface StampDetailViewController()
@property (retain) NSManagedObjectContext *managedObjectContext;
@property (retain) UIBarButtonItem *starButton;
@end

@implementation StampDetailViewController

@synthesize managedObjectContext, stampId, starButton, toolbar;

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context
{
    if (self = [super init]) {
		self.managedObjectContext = context;
    }
    return self;
}

- (UIView *)buildTitleBarWithStamp:(Stamp *)stamp
{
	CGFloat titleBarWidth = [[UIScreen mainScreen] applicationFrame].size.width - 20;
	#define FONT_SIZE 30
	
	// TITLE
	UILabel *titleLabel = [[UILabel alloc] initWithFrame:CGRectMake(70, 0, titleBarWidth - 70, 60)];
	
	//Calculate the expected size based on the font and linebreak mode of your label
	CGSize maximumLabelSize = CGSizeMake(titleLabel.frame.size.width,9999);
	
	CGSize expectedLabelSize = [stamp.title sizeWithFont:[UIFont boldSystemFontOfSize:FONT_SIZE] 
									  constrainedToSize:maximumLabelSize 
										  lineBreakMode:UILineBreakModeWordWrap]; 
	
	// Adjust the label to the new height.
	CGRect newFrame = titleLabel.frame;
	newFrame.size.height = expectedLabelSize.height;
	titleLabel.frame = newFrame;
	
	// Set variables of titleLabel
	[titleLabel setText:stamp.title];
	[titleLabel setTextColor:[UIColor blackColor]];
	[titleLabel setBackgroundColor:[UIColor clearColor]];
	titleLabel.font = [UIFont boldSystemFontOfSize:FONT_SIZE];
	titleLabel.numberOfLines = 0;
	
	
	// IMAGE
	UIImageView *imageLabel = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 60, 60)];
	
	NSString *imageName = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) ? [NSString stringWithFormat:@"e-%@-2x", self.stampId] : [NSString stringWithFormat:@"e-%@", self.stampId];
	
	if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:imageName ofType:@"png"]]) {
		[imageLabel setImage:[UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:imageName ofType:@"png"]]];
	}
	else {
		[imageLabel setImage:[UIImage imageWithContentsOfFile:[NSString stringWithFormat:@"%@/%@.png", [[NSBundle mainBundle] resourcePath], @"endorsementDefault"]]];
	}
	
	// APPLY ELEMENTS
	CGFloat titleBarHeight = (titleLabel.frame.size.height > 60) ? titleLabel.frame.size.height : 60;
	UIView *titleBar = [[UIView alloc] initWithFrame:CGRectMake(10, 10, [[UIScreen mainScreen] applicationFrame].size.width - 20, titleBarHeight)];
	
	[titleBar addSubview:titleLabel];
	[titleLabel release];
	
	[titleBar addSubview:imageLabel];
	[imageLabel release];
	
	return titleBar;
}

- (void)viewWillAppear:(BOOL)animated
{	
	
	Stamp *stamp = [Stamp stampWithId:self.stampId inManagedObjectContext:self.managedObjectContext];
	
	User *user = [User userWithId:stamp.userId inManagedObjectContext:self.managedObjectContext];
	
	UIView *titleBar = [self buildTitleBarWithStamp:stamp];
	
	
	
	
	// USER NAME
	UILabel *userNameLabel = [[UILabel alloc] initWithFrame:CGRectMake(50, 0, [[UIScreen mainScreen] applicationFrame].size.width - 70, 20)];
	[userNameLabel setText:user.name];
	[userNameLabel setBackgroundColor:[UIColor clearColor]];
	userNameLabel.font = [UIFont boldSystemFontOfSize:17];

	
	// USER IMAGE
	UIImageView *userImageLabel = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 40, 40)];
	
	NSString *userImageName = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) ? [NSString stringWithFormat:@"u-%@-2x", user.userId] : [NSString stringWithFormat:@"u-%@", user.userId];
	
	if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:userImageName ofType:@"png"]]) {
		[userImageLabel setImage:[UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:userImageName ofType:@"png"]]];
	}
	else {
		[userImageLabel setImage:[UIImage imageWithContentsOfFile:[NSString stringWithFormat:@"%@/%@.png", [[NSBundle mainBundle] resourcePath], @"endorsementDefault"]]];
	}
	
	// STAMP TIMESTAMP
	UILabel *dateStampedLabel = [[UILabel alloc] initWithFrame:CGRectMake(50, 22, [[UIScreen mainScreen] applicationFrame].size.width - 70, 13)];
	NSDateFormatter *dateFormat = [[NSDateFormatter alloc] init];
	NSDateFormatter *timeFormat = [[NSDateFormatter alloc] init];
	[dateFormat setDateFormat:@"MMM d"];
	[timeFormat setDateFormat:@"h:mm a"];
	[dateStampedLabel setText:[NSString stringWithFormat:@"%@ at %@", [dateFormat stringFromDate:stamp.dateStamped], [timeFormat stringFromDate:stamp.dateStamped]]];
	[dateFormat release];
	[timeFormat release];
	
	[dateStampedLabel setTextColor:[UIColor grayColor]];
	dateStampedLabel.font = [UIFont systemFontOfSize:13];
	
	
	
	// USER MESSAGE
	UILabel *userMessageLabel = [[UILabel alloc] initWithFrame:CGRectMake(50, 40, [[UIScreen mainScreen] applicationFrame].size.width - 70, 140)];
	[userMessageLabel setText:stamp.message];
	userMessageLabel.numberOfLines = 0;
	userMessageLabel.font = [UIFont systemFontOfSize:18];
	
	//Calculate the expected size based on the font and linebreak mode of your label
	CGSize maximumLabelSize = CGSizeMake(userMessageLabel.frame.size.width,9999);
	
	CGSize expectedLabelSize = [stamp.message sizeWithFont:[UIFont systemFontOfSize:18] 
										 constrainedToSize:maximumLabelSize 
											 lineBreakMode:UILineBreakModeWordWrap]; 
	
	// Adjust the label to the new height.
	CGRect newFrame = userMessageLabel.frame;
	newFrame.size.height = expectedLabelSize.height;
	userMessageLabel.frame = newFrame;
	
	
	// USER BAR
	UIView *userBar = [[UIView alloc] initWithFrame:CGRectMake(10, 
															   titleBar.frame.size.height + titleBar.frame.origin.y + 10, 
															   [[UIScreen mainScreen] applicationFrame].size.width - 20, 
															   40 + userMessageLabel.frame.size.height)];
	
	[userBar addSubview:userNameLabel];
	[userNameLabel release];
	
	[userBar addSubview:userImageLabel];
	[userImageLabel release];
	
	[userBar addSubview:dateStampedLabel];
	[dateStampedLabel release];
	
	[userBar addSubview:userMessageLabel];
	[userMessageLabel release];
	
	
	
	CGFloat scrollHeight = userBar.frame.size.height + userBar.frame.origin.y + 10;
//	NSLog(@"%f", scrollHeight);
	
	UIView *userBarB = nil;
	UIView *userBarC = nil;
	
	NSLog(@"stampId: %@", self.stampId);
	if ([self.stampId isEqualToNumber:[NSNumber numberWithInt:201]])
	{
		// Create temporary conversation around Resto
		
		// USER NAME
		UILabel *userNameLabelB = [[UILabel alloc] initWithFrame:CGRectMake(50, 0, [[UIScreen mainScreen] applicationFrame].size.width - 70, 20)];
		[userNameLabelB setText:@"Bart Stein"];
		[userNameLabelB setBackgroundColor:[UIColor clearColor]];
		userNameLabelB.font = [UIFont boldSystemFontOfSize:17];
		
		
		// USER IMAGE
		UIImageView *userImageLabelB = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 40, 40)];
		
		NSString *userImageNameB = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) ? @"u-3-2x" : @"u-3";
		
		if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:userImageNameB ofType:@"png"]]) {
			[userImageLabelB setImage:[UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:userImageNameB ofType:@"png"]]];
		}
		
		// STAMP TIMESTAMP
		UILabel *dateStampedLabelB = [[UILabel alloc] initWithFrame:CGRectMake(50, 22, [[UIScreen mainScreen] applicationFrame].size.width - 70, 13)];
		[dateStampedLabelB setText:@"Dec 5 at 8:24 pm"];
		[dateStampedLabelB setTextColor:[UIColor grayColor]];
		dateStampedLabelB.font = [UIFont systemFontOfSize:13];
		
		
		// USER MESSAGE
		UILabel *userMessageLabelB = [[UILabel alloc] initWithFrame:CGRectMake(50, 40, [[UIScreen mainScreen] applicationFrame].size.width - 70, 140)];
		[userMessageLabelB setText:@"Is there usually a long wait?"];
		userMessageLabelB.numberOfLines = 0;
		userMessageLabelB.font = [UIFont systemFontOfSize:18];
		
		//Calculate the expected size based on the font and linebreak mode of your label
		CGSize maximumLabelSizeB = CGSizeMake(userMessageLabelB.frame.size.width,9999);
		
		CGSize expectedLabelSizeB = [@"Is there usually a long wait?" sizeWithFont:[UIFont systemFontOfSize:18] 
															  constrainedToSize:maximumLabelSizeB
																  lineBreakMode:UILineBreakModeWordWrap]; 
		
		// Adjust the label to the new height.
		CGRect newFrameB = userMessageLabelB.frame;
		newFrameB.size.height = expectedLabelSizeB.height;
		userMessageLabelB.frame = newFrameB;
		
		// USER BAR
		userBarB = [[UIView alloc] initWithFrame:CGRectMake(10, 
															userBar.frame.size.height + userBar.frame.origin.y + 10, 
															[[UIScreen mainScreen] applicationFrame].size.width - 20, 
															40 + userMessageLabelB.frame.size.height)];
		
		[userBarB addSubview:userNameLabelB];
		[userNameLabelB release];
		
		[userBarB addSubview:userImageLabelB];
		[userImageLabelB release];
		
		[userBarB addSubview:dateStampedLabelB];
		[dateStampedLabelB release];
		
		[userBarB addSubview:userMessageLabelB];
		[userMessageLabelB release];
		
		
		
		
		// Create temporary conversation around Resto
		
		// USER NAME
		UILabel *userNameLabelC = [[UILabel alloc] initWithFrame:CGRectMake(50, 0, [[UIScreen mainScreen] applicationFrame].size.width - 70, 20)];
		[userNameLabelC setText:@"Robby Stein"];
		[userNameLabelC setBackgroundColor:[UIColor clearColor]];
		userNameLabelC.font = [UIFont boldSystemFontOfSize:17];
		
		
		// USER IMAGE
		UIImageView *userImageLabelC = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 40, 40)];
		
		NSString *userImageNameC = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) ? @"u-2-2x" : @"u-2";
		
		if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:userImageNameC ofType:@"png"]]) {
			[userImageLabelC setImage:[UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:userImageNameC ofType:@"png"]]];
		}
		
		// STAMP TIMESTAMP
		UILabel *dateStampedLabelC = [[UILabel alloc] initWithFrame:CGRectMake(50, 22, [[UIScreen mainScreen] applicationFrame].size.width - 70, 13)];
		[dateStampedLabelC setText:@"Dec 5 at 10:04 pm"];
		[dateStampedLabelC setTextColor:[UIColor grayColor]];
		dateStampedLabelC.font = [UIFont systemFontOfSize:13];
		
		
		// USER MESSAGE
		UILabel *userMessageLabelC = [[UILabel alloc] initWithFrame:CGRectMake(50, 40, [[UIScreen mainScreen] applicationFrame].size.width - 70, 140)];
		[userMessageLabelC setText:@"We were seated right away, but it did get pretty crowded... I think they take reservations though."];
		userMessageLabelC.numberOfLines = 0;
		userMessageLabelC.font = [UIFont systemFontOfSize:18];
		
		//Calculate the expected size based on the font and linebreak mode of your label
		CGSize maximumLabelSizeC = CGSizeMake(userMessageLabelB.frame.size.width,9999);
		
		CGSize expectedLabelSizeC = [@"We were seated right away, but it did get pretty crowded... I think they take reservations though." sizeWithFont:[UIFont systemFontOfSize:18] 
															  constrainedToSize:maximumLabelSizeC
																  lineBreakMode:UILineBreakModeWordWrap]; 
		
		// Adjust the label to the new height.
		CGRect newFrameC = userMessageLabelC.frame;
		newFrameC.size.height = expectedLabelSizeC.height;
		userMessageLabelC.frame = newFrameC;
		
		// USER BAR
		userBarC = [[UIView alloc] initWithFrame:CGRectMake(10, 
															userBarB.frame.size.height + userBarB.frame.origin.y + 10, 
															[[UIScreen mainScreen] applicationFrame].size.width - 20, 
															40 + userMessageLabelC.frame.size.height)];
		
		[userBarC addSubview:userNameLabelC];
		[userNameLabelC release];
		
		[userBarC addSubview:userImageLabelC];
		[userImageLabelC release];
		
		[userBarC addSubview:dateStampedLabelC];
		[dateStampedLabelC release];
		
		[userBarC addSubview:userMessageLabelC];
		[userMessageLabelC release];
		
		scrollHeight = userBarC.frame.size.height + userBarC.frame.origin.y + 10;
		
	}
	
	
	
	
	UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:CGRectMake(0, 0, [[UIScreen mainScreen] applicationFrame].size.width, [[UIScreen mainScreen] applicationFrame].size.height - 44)];
	scrollView.contentSize = CGSizeMake([[UIScreen mainScreen] applicationFrame].size.width, 
//										[[UIScreen mainScreen] applicationFrame].size.height - 88);
										scrollHeight);
	
	scrollView.contentInset = UIEdgeInsetsMake(0, 0, 44, 0);
	scrollView.bounces = YES;
	scrollView.delegate = self;
	scrollView.backgroundColor = [UIColor clearColor];
	
	[scrollView addSubview:titleBar];
	[scrollView addSubview:userBar];
	[scrollView addSubview:userBarB];
	[scrollView addSubview:userBarC];
	
	[self.view addSubview:scrollView];
	
	// Release objects
	[titleBar release];
	[userBar release];
	[userBarB release];
	[userBarC release];
	[scrollView release];
	
	
	
	/** TOOLBAR **/
	
	toolbar = [UIToolbar new];
	toolbar.barStyle = UIBarStyleDefault;
	[toolbar setFrame:CGRectMake(0, // x-axis
								 [[UIScreen mainScreen] applicationFrame].size.height - 88, // y-axis
								 [[UIScreen mainScreen] applicationFrame].size.width, // width
								 44)]; // height
	
	
	// Check if starred
	NSString *favButtonText = ([stamp.isStarred boolValue]) ? @"★" : @"☆";
	
	// Create button if necessary
	if (!starButton) {
		starButton = [[UIBarButtonItem alloc] initWithTitle:favButtonText 
													 style:UIBarButtonItemStylePlain 
													target:self 
													action:@selector(favClicked)];
		[starButton retain];
	}
	
	UIBarButtonItem *actionButton = nil;
	if ([stamp.stampType isEqual:@"Eat"]) {
		actionButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(actionSheetEat:)];
	} 
	else if ([stamp.stampType isEqual:@"Read"]) {
		actionButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(actionSheetRead:)];
	} 
	else if ([stamp.stampType isEqual:@"Watch"]) {
		actionButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(actionSheetWatch:)];
	} 
	else if ([stamp.stampType isEqual:@"Listen"]) {
		actionButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(actionSheetListen:)];
	} 
	else {
		actionButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(actionSheetDefault:)];
	}
	
	
	
	UIImage *restampButtomImage = nil;
	if ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2)
	{
		// Retina
		restampButtomImage = [UIImage imageWithCGImage:[[UIImage imageNamed:@"48_media-repeat.png"] CGImage] 
											 scale:2.0 
									   orientation:UIImageOrientationUp];
	} else {
		// Normal
		restampButtomImage = [UIImage imageWithCGImage:[[UIImage imageNamed:@"24_media-repeat.png"] CGImage] 
											 scale:1.0 
									   orientation:UIImageOrientationUp];
	}
	
	UIBarButtonItem *restampButton = [[UIBarButtonItem alloc] initWithImage:restampButtomImage
																	  style:UIBarButtonItemStylePlain 
																	 target:self 
																	 action:@selector(alertRestamp)];

	UIBarButtonItem *trashButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemTrash target:self action:@selector(alertTrash)];
	UIBarButtonItem *replyButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemReply target:self action:@selector(alertReply)];
	
	UIBarButtonItem *spaceButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemFlexibleSpace target:self action:nil];
	
	[toolbar setItems:[NSArray arrayWithObjects:starButton, spaceButton, restampButton, spaceButton, trashButton, spaceButton, replyButton, spaceButton, actionButton, nil]];
	
	[self.view addSubview:toolbar];
	
	
	
	
}

// MARK: -
// MARK: ActionSheets

- (void)favClicked 
{	
	if ([starButton.title isEqual:@"★"]) {
		[Stamp toggleStar:[NSNumber numberWithBool:NO] forStampId:self.stampId inManagedObjectContext:self.managedObjectContext];
		starButton.title = @"☆";
		
	}
	else {
		[Stamp toggleStar:[NSNumber numberWithBool:YES] forStampId:self.stampId inManagedObjectContext:self.managedObjectContext];
		starButton.title = @"★";
	}
	
}

- (void)actionSheetDefault:(id)sender
{
	UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil
															 delegate:self 
													cancelButtonTitle:@"Cancel" 
											   destructiveButtonTitle:nil
													otherButtonTitles:@"Share...", @"Visit Website", nil];
	actionSheet.actionSheetStyle = UIActionSheetStyleDefault;
	[actionSheet showInView:self.view]; // show from our table view (pops up in the middle of the table)
	[actionSheet release];
}


- (void)actionSheetEat:(id)sender
{
	UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil
															 delegate:self 
													cancelButtonTitle:@"Cancel" 
											   destructiveButtonTitle:nil
													otherButtonTitles:@"Reserve on OpenTable", @"Share...", @"Visit Website", nil];
	actionSheet.actionSheetStyle = UIActionSheetStyleDefault;
	[actionSheet showInView:self.view]; // show from our table view (pops up in the middle of the table)
	[actionSheet release];
}


- (void)actionSheetRead:(id)sender
{
	UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil
															 delegate:self 
													cancelButtonTitle:@"Cancel" 
											   destructiveButtonTitle:nil
													otherButtonTitles:@"Buy on Amazon", @"Share...", @"Visit Website", nil];
	actionSheet.actionSheetStyle = UIActionSheetStyleDefault;
	[actionSheet showInView:self.view]; // show from our table view (pops up in the middle of the table)
	[actionSheet release];
}


- (void)actionSheetWatch:(id)sender
{
	UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil
															 delegate:self 
													cancelButtonTitle:@"Cancel" 
											   destructiveButtonTitle:nil
													otherButtonTitles:@"Buy on Amazon", @"Buy on iTunes", @"Share...", @"Visit Website", nil];
	actionSheet.actionSheetStyle = UIActionSheetStyleDefault;
	[actionSheet showInView:self.view]; // show from our table view (pops up in the middle of the table)
	[actionSheet release];
}


- (void)actionSheetListen:(id)sender
{
	UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil
															 delegate:self 
													cancelButtonTitle:@"Cancel" 
											   destructiveButtonTitle:nil
													otherButtonTitles:@"Buy on iTunes", @"Share...", @"Visit Website", nil];
	actionSheet.actionSheetStyle = UIActionSheetStyleDefault;
	[actionSheet showInView:self.view]; // show from our table view (pops up in the middle of the table)
	[actionSheet release];
}

- (void)alertTrash
{
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"DEMO" message:@"[Delete Stamp]" delegate:self cancelButtonTitle:@"Cancel" otherButtonTitles:nil] autorelease];
    // optional - add more buttons:
    [alert show];
}

- (void)alertReply
{
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"DEMO" message:@"[Comment on Stamp]" delegate:self cancelButtonTitle:@"Cancel" otherButtonTitles:nil] autorelease];
    // optional - add more buttons:
    [alert show];
}

- (void)alertRestamp
{
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"DEMO" message:@"[Restamp]" delegate:self cancelButtonTitle:@"Cancel" otherButtonTitles:nil] autorelease];
    // optional - add more buttons:
    [alert show];
}

/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView {
}
*/

/*
// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
    [super viewDidLoad];
}
*/

/*
// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations.
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}
*/

// MARK: -

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
}

- (void)viewDidUnload {
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
	self.toolbar = nil;
}


- (void)dealloc {
	[toolbar release];
    [super dealloc];
}


@end
