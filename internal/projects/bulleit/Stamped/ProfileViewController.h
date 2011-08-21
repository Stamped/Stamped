//
//  ProfileViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@class User;
@class UserImageView;

@interface ProfileViewController : STReloadableTableViewController <RKObjectLoaderDelegate>

@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIButton* cameraButton;
@property (nonatomic, retain) IBOutlet UILabel* creditCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* followerCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* followingCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* fullNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* usernameLocationLabel;
@property (nonatomic, retain) IBOutlet UILabel* bioLabel;
@property (nonatomic, retain) IBOutlet UIImageView* shelfImageView;

@property (nonatomic, retain) User* user;

- (IBAction)creditsButtonPressed:(id)sender;
- (IBAction)followersButtonPressed:(id)sender;
- (IBAction)followingButtonPressed:(id)sender;
- (IBAction)cameraButtonPressed:(id)sender;
@end
