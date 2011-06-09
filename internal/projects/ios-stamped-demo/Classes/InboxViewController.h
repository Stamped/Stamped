//
//  InboxViewController.h
//  Stamped
//
//  Created by Kevin Palms on 2/8/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreData/CoreData.h>
#import "StampCell.h"
#import "FilterViewController.h"

@interface InboxViewController : UIViewController < NSFetchedResultsControllerDelegate, 
													UITableViewDelegate, 
													UITableViewDataSource, 
													FilterViewDelegate > 
{
	UITableView					*inboxTableView;
	NSPredicate					*normalPredicate;
	NSFetchedResultsController	*fetchedResultsController;
	UISegmentedControl			*segmentedControl;
	NSInteger					activeSegmentedControl;
}

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context;

@property (nonatomic, retain) IBOutlet UITableView *inboxTableView;
@property (retain) NSFetchedResultsController *fetchedResultsController;

@end
