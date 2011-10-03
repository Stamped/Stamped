//
//  EditProfileViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/3/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "StampCustomizerViewController.h"

@class User;
@class STImageView;

@interface EditProfileViewController : UIViewController <StampCustomizerViewControllerDelegate>

@property (nonatomic, retain) User* user;
@property (nonatomic, retain) IBOutlet UIImageView* stampImageView;
@property (nonatomic, retain) IBOutlet STImageView* userImageView;

- (IBAction)settingsButtonPressed:(id)sender;
- (IBAction)editStampButtonPressed:(id)sender;

@end
