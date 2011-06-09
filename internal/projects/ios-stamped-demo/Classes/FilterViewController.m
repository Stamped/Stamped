    //
//  FilterViewController.m
//  Stamped
//
//  Created by Kevin Palms on 2/10/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "FilterViewController.h"

@interface FilterViewController()
@property (retain) NSManagedObjectContext *managedObjectContext;
@end

@implementation FilterViewController

@synthesize managedObjectContext, delegate;

// MARK: -
// MARK: Initialization

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context
{
    if (self = [super init]) {
		self.managedObjectContext = context;
    }
    return self;
}



// MARK: -
// MARK: View
- (void)viewWillAppear:(BOOL)animated
{	
	if ([self.parentViewController isKindOfClass:[UINavigationController class]])
	{
		//				// TODO: Get title / cancel button working
		//UINavigationController *nc = [[UINavigationController alloc] initWithRootViewController:fvc];
		self.title = @"Apply Filter";
		
		UIBarButtonItem *cancelButton =
		[[UIBarButtonItem alloc] initWithTitle: @"Cancel"
										 style: UIBarButtonItemStylePlain
										target: self.delegate
										action: @selector(dismissModal:)];
		self.navigationItem.leftBarButtonItem = cancelButton;
		[cancelButton release];
		
	}
	
	UIView *filterView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, [[UIScreen mainScreen] applicationFrame].size.width, [[UIScreen mainScreen] applicationFrame].size.height)];
	[filterView setBackgroundColor:[UIColor whiteColor]];
	
	
//	UIButton *button = [[UIButton alloc] initWithFrame:CGRectMake (20, 20, 140, 40)];
//	[button addTarget:self.delegate action:@selector(dismissModal:) forControlEvents:UIControlEventTouchUpInside];
//	[button setBackgroundColor:[UIColor redColor]];
//	button.titleLabel.text = @"Dismiss";
//	
//	[sampleModal addSubview:button];
//	[button release];
	
	
	
	// Eat
	UIButton *fbEat = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	fbEat.frame = CGRectMake(10, 10, 93, 93);
	[fbEat addTarget:self action:@selector(applyFilterEat) forControlEvents:UIControlEventTouchUpInside];
	[fbEat setBackgroundColor:[UIColor whiteColor]];
	[fbEat setTitle:@"Eat" forState:UIControlStateNormal];
	[filterView addSubview:fbEat];
	
	
	// Drink
	UIButton *fbDrink = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	fbDrink.frame = CGRectMake(113, 10, 93, 93);
	[fbDrink addTarget:self action:@selector(applyFilterDrink) forControlEvents:UIControlEventTouchUpInside];
	[fbDrink setBackgroundColor:[UIColor whiteColor]];
	[fbDrink setTitle:@"Drink" forState:UIControlStateNormal];
	[filterView addSubview:fbDrink];
	
	
	// Play
	UIButton *fbPlay = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	fbPlay.frame = CGRectMake(216, 10, 93, 93);
	[fbPlay addTarget:self action:@selector(applyFilterPlay) forControlEvents:UIControlEventTouchUpInside];
	[fbPlay setBackgroundColor:[UIColor whiteColor]];
	[fbPlay setTitle:@"Play" forState:UIControlStateNormal];
	[filterView addSubview:fbPlay];
	
	
	// Read
	UIButton *fbRead = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbRead setBackgroundColor:[UIColor whiteColor]];
	fbRead.frame = CGRectMake(10, 143, 93, 93);
	[fbRead addTarget:self action:@selector(applyFilterRead) forControlEvents:UIControlEventTouchUpInside];
	[fbRead setTitle:@"Read" forState:UIControlStateNormal];
	[filterView addSubview:fbRead];
	
	
	// Watch
	UIButton *fbWatch = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbWatch setBackgroundColor:[UIColor whiteColor]];
	fbWatch.frame = CGRectMake(113, 143, 93, 93);
	[fbWatch addTarget:self action:@selector(applyFilterWatch) forControlEvents:UIControlEventTouchUpInside];
	[fbWatch setTitle:@"Watch" forState:UIControlStateNormal];
	[filterView addSubview:fbWatch];
	
	
	// Listen
	UIButton *fbListen = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbListen setBackgroundColor:[UIColor whiteColor]];
	fbListen.frame = CGRectMake(216, 143, 93, 93);
	[fbListen addTarget:self action:@selector(applyFilterListen) forControlEvents:UIControlEventTouchUpInside];
	[fbListen setTitle:@"Listen" forState:UIControlStateNormal];
	[filterView addSubview:fbListen];
	[filterView addSubview:fbPlay];
	
	
	// Buy
	UIButton *fbBuy = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbBuy setBackgroundColor:[UIColor whiteColor]];
	fbBuy.frame = CGRectMake(10, 276, 93, 93);
	[fbBuy addTarget:self action:@selector(applyFilterBuy) forControlEvents:UIControlEventTouchUpInside];
	[fbBuy setTitle:@"Buy" forState:UIControlStateNormal];
	[filterView addSubview:fbBuy];
	
	
	// Wear
	UIButton *fbWear = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbWear setBackgroundColor:[UIColor whiteColor]];
	fbWear.frame = CGRectMake(113, 276, 93, 93);
	[fbWear addTarget:self action:@selector(applyFilterWear) forControlEvents:UIControlEventTouchUpInside];
	[fbWear setTitle:@"Wear" forState:UIControlStateNormal];
	[filterView addSubview:fbWear];
	
	
	// Visit
	UIButton *fbVisit = [UIButton buttonWithType:UIButtonTypeRoundedRect];
	[fbVisit setBackgroundColor:[UIColor whiteColor]];
	fbVisit.frame = CGRectMake(216, 276, 93, 93);
	[fbVisit addTarget:self action:@selector(applyFilterVisit) forControlEvents:UIControlEventTouchUpInside];
	[fbVisit setTitle:@"Visit" forState:UIControlStateNormal];
	[filterView addSubview:fbVisit];
	
	
	
	[self.view addSubview:filterView];
	[filterView release];
}

// MARK: -
// MARK: Filters

- (void)applyFilterEat
{
	[self.delegate applyFilterOnStampType:@"Eat"];
}

- (void)applyFilterDrink
{
	[self.delegate applyFilterOnStampType:@"Drink"];
}

- (void)applyFilterPlay
{
	[self.delegate applyFilterOnStampType:@"Play"];
}

- (void)applyFilterRead
{
	[self.delegate applyFilterOnStampType:@"Read"];
}

- (void)applyFilterWatch
{
	[self.delegate applyFilterOnStampType:@"Watch"];
}

- (void)applyFilterListen
{
	[self.delegate applyFilterOnStampType:@"Listen"];
}

- (void)applyFilterBuy
{
	[self.delegate applyFilterOnStampType:@"Buy"];
}

- (void)applyFilterWear
{
	[self.delegate applyFilterOnStampType:@"Wear"];
}

- (void)applyFilterVisit
{
	[self.delegate applyFilterOnStampType:@"Visit"];
}


// MARK: -
// MARK: Unload

/*
// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations.
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}
*/

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
}

- (void)viewDidUnload {
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}


- (void)dealloc {
    [super dealloc];
}


@end
