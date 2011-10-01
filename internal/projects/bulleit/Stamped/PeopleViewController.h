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

@interface PeopleViewController : STReloadableTableViewController <RKObjectLoaderDelegate>

@property (nonatomic, retain) IBOutlet UserImageView* currentUserView;
@property (nonatomic, retain) IBOutlet UIImageView* userStampImageView;
@property (nonatomic, retain) IBOutlet UILabel* userFullNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* userScreenNameLabel;
@property (nonatomic, retain) IBOutlet UIButton* addFriendsButton;
@property (nonatomic, retain) IBOutlet UINavigationController* settingsNavigationController;

@end
