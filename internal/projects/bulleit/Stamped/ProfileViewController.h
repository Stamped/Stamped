//
//  ProfileViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@class User;
@class UserImageView;

@interface ProfileViewController : UIViewController <RKObjectLoaderDelegate,
                                                     RKRequestDelegate,
                                                     UITableViewDelegate,
                                                     UITableViewDataSource>

@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIButton* cameraButton;
@property (nonatomic, retain) IBOutlet UILabel* creditCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* followerCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* followingCountLabel;
@property (nonatomic, retain) IBOutlet UILabel* fullNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* usernameLocationLabel;
@property (nonatomic, retain) IBOutlet UILabel* bioLabel;
@property (nonatomic, retain) IBOutlet UIImageView* shelfImageView;
@property (nonatomic, retain) IBOutlet UIView* toolbarView;
@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet UIButton* followButton;
@property (nonatomic, retain) IBOutlet UIButton* unfollowButton;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* followIndicator;

@property (nonatomic, retain) User* user;

- (IBAction)followButtonPressed:(id)sender;
- (IBAction)unfollowButtonPressed:(id)sender;
- (IBAction)creditsButtonPressed:(id)sender;
- (IBAction)followersButtonPressed:(id)sender;
- (IBAction)followingButtonPressed:(id)sender;
- (IBAction)cameraButtonPressed:(id)sender;
@end
