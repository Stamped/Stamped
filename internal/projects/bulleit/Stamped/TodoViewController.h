//
//  TodoViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/19/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STTableViewController.h"
#import "TodoTableViewCell.h"

@protocol TodoViewControllerDelegate
- (void)displaySearchEntities;
@end

@interface TodoViewController : STTableViewController <RKObjectLoaderDelegate,
                                                       TodoTableViewCellDelegate,
                                                       NSFetchedResultsControllerDelegate,
                                                       MKMapViewDelegate>

@property (nonatomic, assign) id<TodoViewControllerDelegate> delegate;

@end
