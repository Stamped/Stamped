//
//  STUsersViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

@interface STUsersViewController : STTableViewController

- (id)initWithUserIDs:(NSArray*)userIDs;

@property (nonatomic, readwrite, retain) NSDictionary* userIDToStampID;

@end
