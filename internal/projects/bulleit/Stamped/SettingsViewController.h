//
//  SettingsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SettingsViewController : UIViewController <UIActionSheetDelegate>

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;

- (IBAction)doneButtonPressed:(id)sender;
- (IBAction)notificationsButtonPressed:(id)sender;
- (IBAction)logoutButtonPressed:(id)sender;

@end
