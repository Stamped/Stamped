//
//  PeopleViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STTableViewController.h"

@class UserImageView;

@interface PeopleViewController : STTableViewController <UITableViewDelegate,
                                                         UITableViewDataSource,
                                                         RKObjectLoaderDelegate,
                                                         RKRequestDelegate>

@property (nonatomic, retain) IBOutlet UINavigationController* findFriendsNavigationController;

@end
