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

@interface EditProfileViewController : UIViewController <StampCustomizerViewControllerDelegate,
                                                         UIActionSheetDelegate,
                                                         UINavigationControllerDelegate,
                                                         UIImagePickerControllerDelegate,
                                                         UITextFieldDelegate>

@property (nonatomic, retain) User* user;
@property (nonatomic, retain) IBOutlet UIImageView* stampImageView;
@property (nonatomic, retain) IBOutlet STImageView* userImageView;
@property (nonatomic, retain) IBOutlet UITextField* nameTextField;
@property (nonatomic, retain) IBOutlet UITextField* locationTextField;
@property (nonatomic, retain) IBOutlet UITextField* aboutTextField;
@property (nonatomic, retain) IBOutlet UIView* containerView;
@property (nonatomic, retain) IBOutlet UIButton* saveButton;
@property (nonatomic, retain) IBOutlet UIButton* cancelButton;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* saveIndicator;

- (IBAction)saveButtonPressed:(id)sender;
- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)settingsButtonPressed:(id)sender;
- (IBAction)editStampButtonPressed:(id)sender;
- (IBAction)changePhotoButtonPressed:(id)sender;

@end
