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

#import "STStampFilterBar.h"

@class User;

@interface StampListViewController : UIViewController
    <STStampFilterBarDelegate, RKObjectLoaderDelegate, UITableViewDelegate, UITableViewDataSource, MKMapViewDelegate>

@property (nonatomic, retain) IBOutlet STStampFilterBar* stampFilterBar;
@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, assign) BOOL stampsAreTemporary;
@property (nonatomic, retain) User* user;

@end
