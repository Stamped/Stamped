//
//  PeopleViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@class UserImageView;

@interface PeopleViewController : UIViewController <UITableViewDelegate,
                                                    UITableViewDataSource,
                                                    RKObjectLoaderDelegate>

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet UINavigationController* settingsNavigationController;
@property (nonatomic, retain) IBOutlet UINavigationController* findFriendsNavigationController;

@end
