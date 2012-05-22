//
//  SettingsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SettingsViewController : UIViewController <UIActionSheetDelegate> 

@property (nonatomic, retain) UITableView *tableView;
@property (nonatomic, retain) UIViewController* sharingView;

- (IBAction)doneButtonPressed:(id)sender;
- (IBAction)editProfileButtonPressed:(id)sender;
- (IBAction)logoutButtonPressed:(id)sender;
- (IBAction)sharingButtonPressed:(id)sender;
- (IBAction)aboutUsButtonPressed:(id)sender;
- (IBAction)FAQButtonPressed:(id)sender;
- (IBAction)legalButtonPressed:(id)sender;
- (IBAction)feedbackButtonPressed:(id)sender;

@end
