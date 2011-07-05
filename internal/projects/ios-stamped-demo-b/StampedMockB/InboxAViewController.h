//
//  InboxAViewController.h
//  StampedMockB
//
//  Created by Kevin Palms on 6/27/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreData/CoreData.h>
#import "InboxACell.h"

@interface InboxAViewController : UIViewController 
  < NSFetchedResultsControllerDelegate, UITableViewDelegate, UITableViewDataSource >
{
  UITableView *inboxTableView;
  NSFetchedResultsController *fetchedResultsController;
  NSPredicate *normalPredicate;
  
}

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context;

@property (nonatomic, retain) IBOutlet UITableView *inboxTableView;
@property (retain) NSFetchedResultsController *fetchedResultsController;

@end
