//
//  StampListViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STTableViewController.h"

@class User;

@interface StampListViewController : STTableViewController <RKObjectLoaderDelegate,
                                                            MKMapViewDelegate,
                                                            NSFetchedResultsControllerDelegate>
@property (nonatomic, retain) IBOutlet UIView* listView;
@property (nonatomic, retain) User* user;

@end
